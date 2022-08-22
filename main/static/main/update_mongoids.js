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
            if (data['status'] === 'OK') {
                console.log('It went well!')
                // Write message to user
                let message = "Dataset " + jsonToSend["datasetName"] +  " was updated with MongoID " + jsonToSend["mongoId"] +  "."
                document.getElementById("js_message").innerText = message
            }
            else (
                console.log("It dit NOT go well.")
            )
        })
        
    }
}