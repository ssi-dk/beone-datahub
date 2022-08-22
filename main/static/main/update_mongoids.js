document.getElementById('sample_list').addEventListener('click', addOrRemove);

function addOrRemove(event) {
    if (event.target.type === 'checkbox') {
        let message
        let jsonToSend = {
            "username": document.getElementById('username').innerText,
            "datasetName": document.getElementById("dataset_name").innerText,
        }
        jsonToSend["mongoId"] = event.target.id
        if (event.target.checked) {
            jsonToSend["action"] = 'Add'
            message = "Mongo id " + event.target.id + " was added."
        } else {
            jsonToSend["action"] = 'Remove'
            message = "Mongo id " + event.target.id + " was removed."
        }
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
                console.log(message)
                /* Write message to user */
                document.getElementById("js_message").innerText = message
            }
            else (
                console.log("It dit NOT go well.")
            )
        })
        
    }
}