document.getElementById('sample_list').addEventListener('click', addOrRemove);

function addOrRemove(event) {
    if (event.target.type === 'checkbox') {
        let jsonToSend = {
            "username": document.getElementById('username').innerText,
            "datasetName": document.getElementById("dataset_name").innerText,
            "mongoId": event.target.id
        }
        if (event.target.checked) {
            jsonToSend["action"] = 'Add'
        } else {
            jsonToSend["action"] = 'Remove'
        }
        let url = window.location.origin + '/datasets/add_remove_sample/'
        fetch(url, {
            headers:{
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
            },
        })
        .then(response => {
            return response.json() //Convert response to JSON
        })
        .then(data => {
            let message
            if (data['status'] === 'OK') {
                message = "Dataset " + jsonToSend["datasetName"] +  " was updated with MongoID " + jsonToSend["mongoId"] +  "."
                document.getElementById("js_message").innerText = message
            }
            else (
                message = "Dataset " + jsonToSend["datasetName"] +  " was NOT updated with MongoID " + jsonToSend["mongoId"] +  "!"
            )
        })
        
    }
}