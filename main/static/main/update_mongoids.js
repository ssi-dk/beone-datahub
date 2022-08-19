document.getElementById('sample_list').addEventListener('click', addOrRemove);

function addOrRemove(event) {
    if (event.target.type === 'checkbox') {
        let jsonToSend = {
            "datasetName": document.getElementById("dataset_name").innerText,
            "datasetOwner": document.getElementById("dataset_owner").innerText,
        }
        jsonToSend["mongoId"] = event.target.id
        if (event.target.checked) {
            jsonToSend["action"] = 'Add'
        } else {
            jsonToSend["action"] = 'Remove'
        }
        console.log(jsonToSend)
    }
}