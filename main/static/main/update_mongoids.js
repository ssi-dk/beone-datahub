let jsonToSend = {
    "datasetName": document.getElementById("dataset_name").innerText,
    "datasetOwner": document.getElementById("dataset_owner").innerText,
}
console.log(jsonToSend)


document.getElementById("sample_list").addEventListener("click", addOrRemove);

function addOrRemove(event) {
    if (event.target.type === 'checkbox') {
        console.log(event.target.id);
        console.log(event.target.checked);
    }
}