// select file input
const input = document.getElementById('file_upload');

// add event listener
input.addEventListener('change', () => {
    uploadFile(input.files[0]);
});

const uploadFile = (file) => {

  // add file to FormData object
  const fd = new FormData();
  fd.append('file', file);

  // send `POST` request
  fetch('/upload', {
      method: 'POST',
      body: fd
  })
  .then(res => res.json())
  .then(json => console.log(json))
  .then(task => {
    if(task.task_id) {
        getStatus(task.task_id)
    }
  })
  .catch(err => console.error(err));
}


  
  function getStatus(taskID) {
    alert("getStatus(" + taskID + ")")
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
    //   setTimeout(function() {
    //     getStatus(res.task_id);
    //   }, 1000);
    })
    .catch(err => console.log(err));
  }