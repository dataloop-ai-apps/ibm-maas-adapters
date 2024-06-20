import dtlpy as dl
import http.client
import requests
import logging
import json
import ast
import os

logger = logging.getLogger("IBM-API Adapter")


class ModelAdapter(dl.BaseModelAdapter):
    def __init__(self, model_entity: dl.Model, ibm_api_key_name):
        self.api_key = os.environ.get(ibm_api_key_name, None)
        if self.api_key is None:
            raise ValueError(f"Missing API key: {ibm_api_key_name}")
        logger.info(f"Using secret name: {ibm_api_key_name}")

        super().__init__(model_entity)

    def load(self, local_path, **kwargs):
        self.ibm_project_id = self.configuration.get("project_id", None)
        if self.ibm_project_id is None:
            raise ValueError("You must provide project id matched to your api key. "
                             "Add the project id to the model's configuration under 'project_id'.")

        self.ibm_region = self.configuration.get("region", None)
        if self.ibm_region is None:
            raise ValueError("Region not specified in the configuration. Please add a valid region code "
                             "to the model's configuration under 'region'.")
        elif self.ibm_region not in ["us-south", "eu-de", "eu-gb", "jp-osa", "br-sao", "au-syd", "jp-tok", "ca-tor",
                                     "us-east"]:
            raise ValueError(f"Unsupported region code '{self.ibm_region}' specified. "
                             "Supported regions: us-south, eu-de, eu-gb, jp-osa, br-sao, au-syd, jp-tok, "
                             "ca-tor, us-east")

        logger.info(f"Using IBM Cloud region: {self.ibm_region}")

        # Create access token
        resp = requests.post('https://iam.cloud.ibm.com/identity/token',
                             headers={'Content-Type': 'application/x-www-form-urlencoded'},
                             data=f'grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={self.api_key}')
        self.access_token = resp.json()['access_token']

        self.conn_watsonx = http.client.HTTPSConnection(f"{self.ibm_region}.ml.cloud.ibm.com")

    def prepare_item_func(self, item: dl.Item):
        if ('json' not in item.mimetype or
                item.metadata.get('system', dict()).get('shebang', dict()).get('dltype') != 'prompt'):
            raise ValueError('Only prompt items are supported')
        buffer = json.load(item.download(save_locally=False))
        return buffer

    def predict(self, batch, **kwargs):
        headers = {
            'Authorization': "Bearer " + self.access_token,
            'Content-Type': "application/json",
            'Accept': "application/json"
        }

        system_prompt = self.configuration.get("system_prompt", "")

        annotations = []
        for prompt_item in batch:
            collection = dl.AnnotationCollection()
            for prompt_name, prompt_content in prompt_item.get('prompts').items():
                # get latest question
                question = [p['value'] for p in prompt_content if 'text' in p['mimetype']][0]
                nearest_items = [p['nearestItems'] for p in prompt_content if 'metadata' in p['mimetype'] and
                                 'nearestItems' in p]
                if len(nearest_items) > 0:
                    nearest_items = nearest_items[0]
                    # build context
                    context = ""
                    for item_id in nearest_items:
                        context_item = dl.items.get(item_id=item_id)
                        with open(context_item.download(), 'r', encoding='utf-8') as f:
                            text = f.read()
                        context += f"\n{text}"

                    system_prompt += " " + context

                payload = {"model_id": self.configuration.get("model_id"),
                           "input": system_prompt + "Input: " + question + "  Output:",
                           "parameters": {
                               "decoding_method": "greedy",  # decoding_method should be one of sample greedy
                               "max_new_tokens": self.configuration.get("max_new_tokens", 200),
                               "min_new_tokens": self.configuration.get("min_new_tokens", 0),
                               "stop_sequences": self.configuration.get("stop_sequences", []),
                               "repetition_penalty": 1
                           },
                           "project_id": self.ibm_project_id
                           }
                str_payload = json.dumps(payload)

                self.conn_watsonx.request("POST",
                                          "/ml/v1/text/generation?version=2023-05-29",
                                          str_payload,
                                          headers)

                res = self.conn_watsonx.getresponse()
                if res.status != 200:
                    raise Exception(f"Response from client failed! {res.read()}")

                data = ast.literal_eval(res.read().decode("UTF-8"))

                generated_text_chunks = list()
                for chunk in data.get('results', list()):
                    if chunk is not None:
                        generated_text_chunks.append(chunk.get('generated_text', ''))
                full_answer = ' '.join(generated_text_chunks)

                collection.add(
                    annotation_definition=dl.FreeText(text=full_answer),
                    prompt_id=prompt_name,
                    model_info={
                        'name': self.model_entity.name,
                        'model_id': self.model_entity.id,
                        'confidence': 1.0
                    }
                )
            annotations.append(collection)
        return annotations


if __name__ == '__main__':
    dl.setenv('rc')
    ibm_api_key_name = ''
    model = dl.models.get(model_id='')
    item = dl.items.get(item_id='')
    adapter = ModelAdapter(model, '')
    adapter.predict_items(items=[item])
