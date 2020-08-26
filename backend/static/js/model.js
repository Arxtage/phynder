// CSRF protection
var csrftoken = $('meta[name=csrf-token]').attr('content')
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
        }
    }
})

// Main logic
// const MODEL_URL = "{{ url_for('static', filename='model2/model.json') }}"
const CATEGORIES = [
    "Doing other things",  // 0
    "Drumming Fingers",    // 1
    "No gesture",          // 2
    "Pulling Hand In",     // 3
    "Pulling Two Fingers In",     // 4
    "Pushing Hand Away",          // 5
    "Pushing Two Fingers Away",   // 6
    "Rolling Hand Backward",      // 7
    "Rolling Hand Forward",       // 8
    "Shaking Hand",               // 9
    "Sliding Two Fingers Down",   // 10
    "Sliding Two Fingers Left",   // 11
    "Sliding Two Fingers Right",  // 12
    "Sliding Two Fingers Up",     // 13
    "Stop Sign",      // 14
    "Swiping Down",   // 15
    "Swiping Left",   // 16
    "Swiping Right",  // 17
    "Swiping Up",     // 18
    "Thumb Down",     // 19
    "Thumb Up",       // 20
    "Turning Hand Clockwise",         // 21
    "Turning Hand Counterclockwise",  // 22
    "Zooming In With Full Hand",      // 23
    "Zooming In With Two Fingers",    // 24
    "Zooming Out With Full Hand",     // 25
    "Zooming Out With Two Fingers"    // 26
];
const ILLEGAL_ACTIONS = [7, 8, 21, 22, 3];
const HISTORY_LOGIT = true;
const REFINE_OUTPUT = true;

async function getProcessedFrame(webcam, channels_format) {
    /**
     * Captures a frame from the webcam and normalizes it between -1 and 1.
     * Returns a batched image (1-element batch) of shape [1, w, h, c].
     */
    const img = await webcam.capture();  // (224, 224, 3) 0 ~ 255
    if (channels_format == 'channels_first') {
        const processedImg =
          tf.tidy(() => img.transpose([2, 0, 1]).expandDims(0).toFloat().div(255));  // (1, 3, 224, 224) 0 ~ 1.0
        img.dispose();
        return processedImg;
    } else {
        const processedImg =
          tf.tidy(() => img.expandDims(0).toFloat().div(255));  // (1, 224, 224, 3) 0 ~ 1.0
        img.dispose();
        return processedImg;
    }
}

async function process_output(idx_, history) {
    // idx_: the output of current frame
    // history: a list containing the history of predictions
    max_hist_len = 20;  // max history buffer
    // mask out illegal action
    if (ILLEGAL_ACTIONS.includes(idx_)) {
        idx_ = history.slice(-1)[0];
    }
    // use only single no action class
    if (idx_ == 0) {
        idx_ = 2;
    }
    // history smoothing
    if (idx_ != history.slice(-1)[0]) {
        if (history.slice(-1)[0] != history.slice(-2)[0]) {  // and history[-2] == history[-3]):
            idx_ = history.slice(-1)[0];
        }
    }
    history.push(idx_);
    history = history.slice(-max_hist_len);
    return history;
}

async function predict() {
    try {
        const videoElement = document.createElement('video');
        videoElement.width = 224;
        videoElement.height = 224;
        webcam = await tf.data.webcam(videoElement);
//             cam.stop();
//             const webcam = await tf.data.webcam(document.getElementById('webcam'));
    } catch (e) {
        console.log(e);
        document.getElementById('no-webcam').style.display = 'block';
    }
    const model = await tf.loadGraphModel(MODEL_URL);
    var input_tensors = {
        'i0': tf.ones([1, 3, 224, 224]).transpose([0, 2, 3, 1]),
        'i1': tf.ones([1, 3, 55, 55]).transpose([0, 2, 3, 1]),
        'i2': tf.ones([1, 4, 27, 27]).transpose([0, 2, 3, 1]),
        'i3': tf.ones([1, 4, 27, 27]).transpose([0, 2, 3, 1]),
        'i4': tf.ones([1, 8, 13, 13]).transpose([0, 2, 3, 1]),
        'i5': tf.ones([1, 8, 13, 13]).transpose([0, 2, 3, 1]),
        'i6': tf.ones([1, 8, 13, 13]).transpose([0, 2, 3, 1]),
        'i7': tf.ones([1, 12, 13, 13]).transpose([0, 2, 3, 1]),
        'i8': tf.ones([1, 12, 13, 13]).transpose([0, 2, 3, 1]),
        'i9': tf.ones([1, 20, 6, 6]).transpose([0, 2, 3, 1]),
        'i10': tf.ones([1, 20, 6, 6]).transpose([0, 2, 3, 1])
    }  // SPATIAL SHAPES WERE DECREASED BY 1 !!!
    var jest_id = 2;
    var history = [2, 2];
    function InitLogitHistory(size) {
        var x = [];
        for (var i = 0; i < size; ++i) {
            x.push(tf.ones([1, 27]));
        }
        return x;
    }
    var history_logit = InitLogitHistory(12);
    var hist_cyclic_idx = 0;

    function handle_response(response) {
        current_person_id = response["id"];
        var url = response["image"];
        var img = new Image();
        img.src = url;
        img.addEventListener('load', function() {
            var my_image_element = document.getElementById('person_image');
            my_image_element.src = url;
        });
        $('#person_name_large').text(response["name"]);
        $('#person_name').text(response["name"]);
        $('#person_surname').text(response["surname"]);
        $('#person_sex').text(response["sex"]);
        $('#person_description').text(response["name"]);  // !!!
        var person_vk_button = document.getElementById('person_vk_button');
        person_vk_button.setAttribute("onclick", `window.open('https://vk.com/id${current_person_id}', '_blank')`);
    }
    
    const moveOutLeft = [
      { transform: 'rotate(0) translate3D(0, 0, 0)' }, 
      { transform: 'rotate(-45deg) translate3D(-120vw, 0, 0)' }
    ];
    const moveOutRight = [
      { transform: 'rotate(0) translate3D(0, 0, 0)' }, 
      { transform: 'rotate(45deg) translate3D(120vw, 0, 0)' }
    ];
    const moveTiming = {
      duration: 650,
      iterations: 1
    }

    // Runtime loop
    const NUM_FRAMES_UNTIL_ACTION = 10;
    var combo_left = 0;
    var combo_right = 0;
    var combo_drum = 0;
    var current_person_id = "4599928";  // !!!
    const predicting = true;
    var i_frame = 0;
    while (predicting) {
//             console.time('model.predict()');
        tf.engine().startScope();
        tf.disposeVariables();
        var img = await getProcessedFrame(webcam=webcam, channels_format='channels_last');
        if (i_frame % 2 == 0) {
            _ = tf.tidy(() => {
                input_tensors['i0'] = img;
                preds = model.predict(input_tensors);
                tf.dispose(input_tensors);
                // 4,3,5,7,9,2,0,6,8,j,1
                input_tensors['i5'] = tf.keep(preds[0]);
                input_tensors['i4'] = tf.keep(preds[1]);
                input_tensors['i6'] = tf.keep(preds[2]);
                input_tensors['i8'] = tf.keep(preds[3]);
                input_tensors['i10'] = tf.keep(preds[4]);
                input_tensors['i3'] = tf.keep(preds[5]);
                input_tensors['i1'] = tf.keep(preds[6]);
                input_tensors['i7'] = tf.keep(preds[7]);
                input_tensors['i9'] = tf.keep(preds[8]);
                input_tensors['i2'] = tf.keep(preds[10]);
                history_logit[hist_cyclic_idx] = tf.keep(preds[9]);
                hist_cyclic_idx = (hist_cyclic_idx + 1) % history_logit.length;
            });
            if (HISTORY_LOGIT) {
                avg_logit = history_logit.reduce(function(a, b){ return a.add(b); });
                jest_id = await avg_logit.argMax(axis=1).array();
            }
            tf.disposeVariables();
            if (REFINE_OUTPUT) {
                history = await process_output(jest_id, history);
                jest_id = history.slice(-1)[0];
            }
//                 console.log(CATEGORIES[jest_id]);
            if (CATEGORIES[jest_id] == "Drumming Fingers") {
                combo_drum += 1;
            } else {
                combo_drum = 0;
            }
            if (CATEGORIES[jest_id] == "Swiping Left") {
                combo_left += 1;
            } else {
                combo_left = 0;
            }
            if (CATEGORIES[jest_id] == "Swiping Right") {
                combo_right += 1;
            } else {
                combo_right = 0;
            }
            if (combo_left == NUM_FRAMES_UNTIL_ACTION) {
                console.log(`left ${current_person_id}`);
                $.post(
                    "/swipes_new", 
                    {swipe_type: "left", swipe_id: current_person_id}, 
                    handle_response
                );
                document.getElementById("person_card").animate(
                  moveOutLeft, 
                  moveTiming
                );
            }
            if (combo_right == NUM_FRAMES_UNTIL_ACTION) {
                console.log(`right ${current_person_id}`);
                $.post(
                    "/swipes_new", 
                    {swipe_type: "right", swipe_id: current_person_id},
                    handle_response
                );
                document.getElementById("person_card").animate(
                  moveOutRight, 
                  moveTiming
                );
            }
            if (combo_drum == 42) {
                console.log("something");
                var somethingText = `
                    <video autoplay id="some_video" width="640" height="360">
                        <source src="${SOMETHING_SRC}" type="video/mp4">
                    </video>`;     
                $("#something").append(somethingText);
                setTimeout(function () { $("#something").empty(); }, 8000);
            }
        }
        img.dispose()
        await tf.nextFrame();
        i_frame += 1;
        tf.engine().endScope();
//             console.timeEnd('model.predict()');  // prints ~50-60 ms
    }
//         console.log(tf.memory());
}

predict();
