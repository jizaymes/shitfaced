// select file input
const file_upload = document.getElementById('file_upload');

// add event listener
file_upload.addEventListener('change', () => {
    uploadFile(file_upload.files[0]);
});

function getStatus(taskID) {
  fetch(`/tasks/${taskID}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    },
  })
  .then(response => response.json())
  .then(res => {
    console.log(res)
    const html = `
      <tr>
        <td>${taskID}</td>
        <td>${res.task_status}</td>
        <td>${res.task_result}</td>
      </tr>`;
    const newRow = document.getElementById('tasks').insertRow(0);
    newRow.innerHTML = html;

    const taskStatus = res.task_status;
    if (taskStatus === 'SUCCESS' || taskStatus === 'FAILURE') return false;
    setTimeout(function() {
      getStatus(res.task_id);
    }, 1000);
  })
  .catch(err => console.log(err));
}

const uploadFile = (file) => {
  const fd = new FormData();
  fd.append('file', file);

  console.log("Upload File")

  // send `POST` request
  fetch('/upload', {
      method: 'POST',
      body: fd
  })
  .then(response => response.json())
  .then(task => getStatus(task.task_id))
}
