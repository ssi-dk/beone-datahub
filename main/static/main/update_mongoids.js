
// Todo: check this with current Django documentation.
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

document.getElementById('sample_list').addEventListener('click', addOrRemove);

function addOrRemove(event) {
    if (event.target.type === 'checkbox') {
        let jsonToSend = {
            "username": document.getElementById('username').innerText,
            "datasetName": document.getElementById("dataset_name").innerText,
            "datasetKey": document.getElementById("dataset_key").innerText,
            "mongoId": event.target.id
        }
        if (event.target.checked) {
            jsonToSend["action"] = 'Add'
        } else {
            jsonToSend["action"] = 'Remove'
        }
        let url = window.location.origin + '/datasets/add_remove_sample/'
        fetch(url, {
            method: 'POST',
            credentials: 'same-origin',
            headers:{
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken,
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