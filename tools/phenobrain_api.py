import requests
from fake_useragent import UserAgent

import time


ua = UserAgent()

# @tool
def PhenobrainAPITool(query):
    """
    Use the Phenobrain API to search for Essamble results.

    Args:
        query (str): The search query.

    Returns:
        str: The search results or an error message.
    """
    try:
        headers = {'User-Agent': ua.random}
        
        if isinstance(query, str):
            
            url = "https://www.phenobrain.cs.tsinghua.edu.cn/extract-hpo"
            payload = {
                "text": query,
                "method": "HPO/CHPO",
                "threshold": ""
            }

            response = requests.post(url, json=payload, headers=headers, timeout=30)
            task_id = response.json()['TASK_ID']
            
            get_url = f"https://www.phenobrain.cs.tsinghua.edu.cn/query-extract-hpo-result?taskId={task_id}"
            response = requests.get(get_url, headers=headers, timeout=30)
            if response.json()['state'] == 'FAILURE':
                return "Phenobrain: HPO extraction failed."
            hpo_list = response.json()['result']['HPO_LIST']
            print("Phenobrain HPO List: ", hpo_list)
            
        else:
            hpo_list = query
        
        
        pred_url = "https://www.phenobrain.cs.tsinghua.edu.cn/predict?model=Ensemble"
        for hpo in hpo_list:
            pred_url += f"&hpoList[]={hpo}"
        pred_url += "&topk=5"
        
        response = requests.get(pred_url, headers=headers, timeout=30)
        if response.status_code != 200:
            print(f"Phenobrain Failed Code: {response.status_code}")
            return "Phenobrain: API returned an error."
        task_id = response.json()['TASK_ID']
        
        get_url = f"https://www.phenobrain.cs.tsinghua.edu.cn/query-predict-result?taskId={task_id}"
        
        max_retries = 10
        for _ in range(max_retries):
            response = requests.get(get_url, headers=headers, timeout=30)
            if response.status_code == 200:
                result = response.json()
                state = result.get("state", "").lower()

                if state == "success":
                    print("Phenobrain Search Success!")
                    phenobrain_result = result['result']
                    break
                else:
                    print("Phenobrain Processing...")
                    time.sleep(2)
            else:
                print(f"Failed Code: {response.status_code}")
                return "Phenobrain: API polling failed."
        else:
            return "Phenobrain: API timed out after polling."
            
        disease_list = [i['CODE'] for i in phenobrain_result]
            
        disease_url = "https://www.phenobrain.cs.tsinghua.edu.cn/disease-list-detail"
        disease_payload = {
            "diseaseList": disease_list
        }
        
        response = requests.post(disease_url, json=disease_payload, headers=headers, timeout=30)
        
        results = response.json()
        disease_list_phenobrain = []
        for result in results.values():
            disease_list_phenobrain.append(result['ENG_NAME'] + ' ('+ ' '.join(result['SOURCE_CODES']) + ')')

        return f"Phenobrain gives related diseases about the patient: " + ", ".join(disease_list_phenobrain)

    except Exception as e:
        print(f"[LOG] Phenobrain API failed: {e}")
        return "Phenobrain: API temporarily unavailable. Proceeding without Phenobrain results."




if __name__ == '__main__':
    print(PhenobrainAPITool("Malar flattening, Micrognathia, Preauricular skin tag, Conductive hearing impairment, Atresia of the external auditory canal,"))
