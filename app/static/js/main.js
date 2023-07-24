// select file input
const file_upload = document.getElementById('file_upload');

// add event listener
file_upload.addEventListener('change', () => {
  uploadFile(file_upload.files[0]);
});


function openModal() {
  // document.getElementById("backdrop").style.display = "block"
  document.getElementById("image_modal").style.display = "block"
  document.getElementById("img_modal_result").src = document.getElementById("img_result").src
  document.getElementById("image_modal").classList.add("show")
}
function closeModal() {
  // document.getElementById("backdrop").style.display = "none"
  document.getElementById("image_modal").style.display = "none"
  document.getElementById("image_modal").classList.remove("show")
}
// Get the modal
const modal = document.getElementById('image_modal');

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == modal) {
    closeModal()
  }
}



const uploadFile = (file) => {
  if(!['image/jpeg', 'image/png', 'image/gif', 'image/heic'].includes(file.type))
	{
    setError("Invalid File Type");
    return;
	}

	if(file.size > 4194304)
	{
    setError("Invalid File Size. Max is 4MB");
    return;
	}

  clearNotificationArea();

  const fd = new FormData();
  fd.append('file_upload', file);
  fd.append('selected_emoji', document.querySelector("[name=selected_emoji]:checked").value);

  // send `POST` request
  fetch('/upload', {
      method: 'POST',
      body: fd
  })
  .then(response => response.json())
  .then(data => {
    if(data.error) {
      setError(data.error)
      return;
    }

    toggleUploadAndPendingAreas();

    if(data.record_id) { 
      // Already exists so lets just do that and move on. 
      setImage(data.record_id, "Hey, we've already done this one before. This is what it looks like");
      return
    }
 
    if(data.task_id) {
      getStatus(data.task_id);
    }
  })
  .catch(error => {
    console.error(error)
    setError(error)
  })
}

function clearNotificationArea()
{
  setError("")
  setSuccess("")
}

function setError(text) {
  document.getElementById('error_area').innerHTML = text

  if(text) {
    document.getElementById('error_area').style = "display: block;"
  } else {
    document.getElementById('error_area').style = "display: none;"
  }
}
function setSuccess(text) {
  document.getElementById('success_area').innerHTML = text

  if(text) {
    document.getElementById('success_area').style = "display: block;"
  } else {
    document.getElementById('success_area').style = "display: none;"
  }
}



function setImage(record_id, msg) {
  togglePendingAreaAndResultsAreas();
  setSuccess(msg)

  const html = `
  <div class="modal" id="image_modal" tabindex="-1" aria-labelledby="image_modal_label" aria-modal="true" role="dialog">
    
  <div class="modal-dialog modal-xl modal-dialog-scrollable" role="document">
      <div class="modal-content">
          <div class="modal-header">
              <h4 class="modal-title" id="image_modal_label"></h4>
              <button type="button" class="btn-close" onclick="closeModal()"></button>
          </div>
          <div class="modal-body">
            <img id="img_modal_result" style="width: 100%;">
          </div>
          <div class="modal-footer">
              <button type="button" class="btn btn-secondary" onclick="closeModal()">Close</button>
          </div>
      </div>
  </div>
  </div>

  <div class="row p-2 pb-0 pe-lg-0 pt-sm-2 align-items-center rounded-2 border shadow-lg mx-auto">
    <p class="text-center"><img class="show-img img-responsive rounded border" id="img_result" src="get_shitfaced/${record_id}" alt="Shitfaced record ${record_id}" style="width: 100%; max-width: 500px;" onClick='openModal();'></p>
    <p><button type="button" class="btn btn-primary btn-sm fw-bold position-center" onClick='location.reload();'>Start Over</button></p>
  </div>
  `
  
  document.getElementById("shitface_image_area").innerHTML = html

  return true;
}


function getStatus(taskID) {
  fetch(`/tasks/${taskID}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    },
  })
  .then(response => response.json())
  .then(res => {
    if (res.task_status === 'FAILURE') {
      togglePendingAndErrorAreas()
      setError("Failed due to : " + res.task_result)
      return false;
    } else if (res.task_result == "False") {
      togglePendingAndErrorAreas()
      setError("Failed due to a bad image or a problem")
      return false;
    } else if (res.task_status === 'SUCCESS') {
      setImage(res.task_result,"");
      return true;
    }

    // PENDING, just loop and check back in a second
    setTimeout(function() {
      getStatus(taskID);
    }, 1000);
  })
  .catch(err => console.log(err));
}


function togglePendingAreaAndResultsAreas() {
  document.getElementById('upload_area').style = "display: none;";  
  document.getElementById('pending_area').style = "display: none;";
  document.getElementById('results_area').style = "display: block;";
}

function toggleUploadAndPendingAreas() {
  document.getElementById('upload_area').style = "display: none;";
  document.getElementById('pending_area').style = "display: block;";
}

function togglePendingAndErrorAreas() {
  document.getElementById('pending_area').style = "display: none;";
  document.getElementById('upload_area').style = "display: block;";
}