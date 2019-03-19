function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

function request_prediction(){
  const Http = new XMLHttpRequest();
  const url='http://127.0.0.1:5000/classify';
  Http.open("GET", url, true);
  Http.send();
  Http.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
          obj = JSON.parse(Http.responseText);
          console.log(obj);
          clearUI()

          if(obj.hasOwnProperty('img_lables'))
          {
            displayBuffer(obj.img_lables);
          }
          else
          {
            document.getElementById("buffer_div").innerHTML = "<br><p class=\"text-center\">All mic buffers are empty</p>"
            //resetCounter()
          }

          
          for (mic in obj)
          {   
            if( mic != 'img_lables')
            {
              document.getElementById('prediction').innerHTML += '<hr>'
              var predicted_speaker = "";
              var maxValue = 0;
              for (speaker in obj[mic])
              {
                  if (obj[mic][speaker] > maxValue)
                  {
                      predicted_speaker = speaker
                      maxValue = obj[mic][speaker];   
                  }
              }
              document.getElementById('prediction').innerHTML += '<b>' + mic + '</b> ' + ' scores:<br>';
              document.getElementById(mic).textContent =(capitalizeFirstLetter(predicted_speaker));
              add_speaker(mic,predicted_speaker)
              displayBuffer()
              
              for (speaker in obj[mic])
              {   
                  if (speaker === predicted_speaker) 
                  {
                      document.getElementById('prediction').innerHTML += '&nbsp;&nbsp;<b>'+capitalizeFirstLetter(speaker) +': '+ (obj[mic][speaker]).toFixed(4) + '</b><br>';
                  }
                  else
                  {
                      document.getElementById('prediction').innerHTML += '&nbsp;&nbsp;' + capitalizeFirstLetter(speaker) +': '+ (obj[mic][speaker]).toFixed(4) + '</br>';
                  }
              }
            }
          } 
      }
  }
}
var myVar = setInterval(request_prediction, 3000);

function showClearSpec()
{
  document.getElementById("source_spectrogram").style.display="none";
  document.getElementById("destination_spectrogram").style.display="block";
}

function showOriginSpec()
{
  document.getElementById("source_spectrogram").style.display="block";
  document.getElementById("destination_spectrogram").style.display="none";
}

function displayBuffer(image_lables)
{
  for (mic in image_lables)
  {
    document.getElementById("buffer_div").innerHTML += '<a>&nbsp;&nbsp;<b>' + mic + '</b> buffer: </a>';
    for (i = 0; i < 5; i++) { 
      image_name = "spectrogram_"+i+".jpg"
      var img = document.createElement("img");
      img.src = "real_time\\"+mic+"\\"+image_name;
      if(image_lables[mic] === image_name)
      {
        img.classList = "border border-danger";
      }
      document.getElementById("buffer_div").appendChild(img)
    }
    document.getElementById("buffer_div").innerHTML += find_most_likely_speakers(mic) + "<br>"
  }
}

function clearUI()
{
  document.getElementById('prediction').innerHTML = "";
  document.getElementById("buffer_div").innerHTML = "";
  for (i =0; i<4; i++)
  {
      mic_name = "mic_" + i;
      document.getElementById(mic_name).textContent =(mic_name);
  }
}

speaker_counter = {}
function add_speaker(mic_ref,speaker_name)
{
  if (!speaker_counter.hasOwnProperty(mic_ref))
  {
    speaker_counter[mic_ref] = {}
  }
  if (!speaker_counter[mic_ref].hasOwnProperty(speaker_name))
  {
    speaker_counter[mic_ref][speaker_name] = 1
  }
  else
  {
    speaker_counter[mic_ref][speaker_name] +=1;
  }
}

function resetCounter()
{
  speaker_counter = {}
}

function find_most_likely_speakers(mic_ref)
{
  most_likely_speaker = "";
  max_count = 0;
  total_count = 0;
  for (speaker in speaker_counter[mic_ref])
  {
    if (speaker_counter[mic_ref][speaker] > max_count)
    {
      max_count = speaker_counter[mic_ref][speaker];
      most_likely_speaker = speaker;
    }
    total_count += speaker_counter[mic_ref][speaker];
  }
  confidence = (max_count/total_count)*100
  prediction_string = ""
  start_prediction_delay = 4;
  if (total_count > start_prediction_delay)
  {
    prediction_string = " <i> <b>" + capitalizeFirstLetter(most_likely_speaker) + "</b> (confidence: "+confidence.toFixed(1)+"%)</i>"
  }
  else
  {
    prediction_string = "<i> Calculating most likely speaker " + total_count + "/" + start_prediction_delay + " ...</i>"
  }
  return prediction_string;
}