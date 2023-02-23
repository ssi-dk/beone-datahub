
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
        let strParts = event.target.id.split('.')
        let mongoId = {'name': strParts[1]}
        console.log(mongoId)
        let dataToSend = {
            "username": document.getElementById('username').innerText,
            "datasetName": document.getElementById("dataset_name").innerText,
            "datasetKey": document.getElementById("dataset_key").innerText,
            "mongoId": mongoId
        }
        if (event.target.checked) {
            dataToSend["action"] = 'add'
        } else {
            dataToSend["action"] = 'remove'
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
            body: JSON.stringify(dataToSend) 
        })
        .then(response => {
            return response.json()
        })
        .then(data => {
            console.log(data)
            document.getElementById("messages").style.display = "block"
            let message
            if (data.status === 'OK') {
                message = '<li>' + data.message + '</li>'
            } else {
                message = '<li class="error">ERROR: ' + data.message + '</li>'
            }
            document.getElementById("message-list").innerHTML = document.getElementById("message-list").innerHTML + message
        })
        
    }
}