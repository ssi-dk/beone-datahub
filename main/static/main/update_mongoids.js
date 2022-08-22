document.getElementById('sample_list').addEventListener('click', addOrRemove);

function addOrRemove(event) {
    if (event.target.type === 'checkbox') {
        let message
        let jsonToSend = {
            "datasetName": document.getElementById("dataset_name").innerText,
            "datasetOwner": document.getElementById("dataset_owner").innerText,
        }
        jsonToSend["mongoId"] = event.target.id
        if (event.target.checked) {
            jsonToSend["action"] = 'Add'
            message = "Mongo id " + event.target.id + " was added."
        } else {
            jsonToSend["action"] = 'Remove'
            message = "Mongo id " + event.target.id + " was removed."
        }
        console.log(message)
        document.getElementById("js_message").innerText = message
        let url = window.location.origin + '/datasets/add_remove_sample/'
        console.log(url)
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
            }
            else (
                console.log("It dit NOT go well.")
            )
        })
        
    }
}