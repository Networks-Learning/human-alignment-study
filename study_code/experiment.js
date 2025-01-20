/* initialize jsPsych */
var jsPsych = initJsPsych({
    show_progress_bar: true,
    auto_update_progress_bar: false
});

// capture info from Prolific
var level = jsPsych.data.getURLVariable('LEVEL');
var game_batch = jsPsych.data.getURLVariable('GAME_BATCH');
var subject_id = jsPsych.data.getURLVariable('PROLIFIC_PID');
var study_id = jsPsych.data.getURLVariable('STUDY_ID');
var session_id = jsPsych.data.getURLVariable('SESSION_ID');

//completion URL for prolific
// var completion_URL = "";

var level_string = `level_${level}`;

const EXPERIMENT_FILES = {  
    INSTRUCTIONS: 'materials/instructions.json',
    GAMES: `materials/games_${level_string}/${game_batch}.json`,
    ATTENTION_TESTS: "materials/attention_tests.json",
    CARDS: "materials/cards.json",
    ALIGNMENT_ALG: "materials/alignment_alg.json"
  };

var points = 0;
jsPsych.data.addProperties({
    level_name: level_string,
    study_id: study_id,
    game_batch: game_batch
  });
var image_size = [80, 120]
var nr_trials = 24
var overall_trials =  7 * (nr_trials+4) + 10
var played_rounds = -1
var slider_size = 350
var duration = 2000

var instructions = {};
var cards = {};
var games = {};
var attention_tests = {};
var alignment_alg = {}


/* function to draw card from game pile */
function randomDrawn(game_pile, initial_decision, final_decision, example=false){
    var card = jsPsych.randomization.sampleWithoutReplacement(game_pile, 1)[0];
    var card_color = NaN
    played_rounds +=1
    if (["hearts","diamonds"].some(v => card.includes(v))) {
        card_color = "Red" ;
    }else if (["clubs","spades"].some(v => card.includes(v))){
        card_color = "Black" ;
    }
    var return_string = `<p> Card Picked:<br><br></p>`+`<img src=${card}  class="center-small"></img>`

    return_string +=`<p> <br>Your initial bet was <span class=\"${initial_decision}\">${initial_decision}</span>. <br> Your final bet was <span class=\"${final_decision}\">${final_decision}</span>.</p>`
 
    if (final_decision == card_color) {
        points += 1
        return_string +=`<p><br>You <span class=\"orange\">WON 1 </span> point!<br><br></p>`;
    }  else {
        points -= 1
        return_string +=`<p><br>You <span class=\"orange\">LOST 1 </span> point!<br><br></p>`
    }
    
    if (example){
        points=0
        //played_rounds=0
        return return_string
    }

    return return_string + `You have <span class=\"orange\"> earned ${points} point(s) from ${played_rounds} round(s) </span> until now.<br><br></p>`; 
} 

/* create timeline */
var timeline = [];

/* preload card images */
await fetch(EXPERIMENT_FILES.CARDS).then(response => response.json()).then( data => cards = data)
var preload = {
    type: jsPsychPreload,
    images: cards,
    on_finish: function(data){
        jsPsych.setProgressBar(0);
    }
};
timeline.push(preload);

/* get instructions from file */
await fetch(EXPERIMENT_FILES.INSTRUCTIONS).then(response => response.json()).then( data => instructions = data)

/* get games from file */
await fetch(EXPERIMENT_FILES.GAMES).then(response => response.json()).then( data => games = data)

/* get attention_tests from file */
await fetch(EXPERIMENT_FILES.ATTENTION_TESTS).then(response => response.json()).then( data => attention_tests = data)

/* get alignment algorithm from file */
await fetch(EXPERIMENT_FILES.ALIGNMENT_ALG).then(response => response.json()).then( data => alignment_alg = data)

var games_shuffled = jsPsych.randomization.shuffle(games);


/* display instruction messages */

var enter_fullscreen = {
    type: jsPsychFullscreen,
    fullscreen_mode: true,
    message: instructions.welcome,
    on_finish: function(data){
        jsPsych.setProgressBar(data.trial_index/overall_trials);
    }
  }
timeline.push(enter_fullscreen)

var consent = {
    type: jsPsychHtmlButtonResponse,
    stimulus: instructions.consent,
    choices: ['Consent >'],
    margin_vertical: '100px',
    data: {
        task: 'consent'
    },
    on_finish: function(data){
        jsPsych.setProgressBar(data.trial_index/overall_trials);
    }
}; 
timeline.push(consent)

timeline.push({
    type: jsPsychInstructions,
    pages: instructions.instructions, 
    show_clickable_nav: true,
    on_finish: function(data){
        jsPsych.setProgressBar(data.trial_index/overall_trials);
    }
});


var size_check = {
    type: jsPsychBrowserCheck,
    inclusion_function: (data) => {
        if (data.width/4 >= 350 && data.width/4 < 800){
            slider_size = (Math.round(data.width/4));
        }else if (data.width/3 >= 350 && data.width/3 < 800){
            slider_size = (Math.round(data.width/3));
        }
        image_size = (Math.round(data.width/21), Math.round(data.height/11));
        return true;
    }
};
timeline.push(size_check)


/* Definition of page*/
var grid_intro = attention_tests[0]
var grid_AI_intro = attention_tests[1]; 



var game_pile = {
    type: jsPsychHtmlButtonResponse,
    stimulus: function(){
        return jsPsychVslGridScene.generate_stimulus(jsPsych.timelineVariable('game'), image_size)},
    save_trial_parameters: {stimulus_duration: true},
    trial_duration: duration,
    choices: [],
    data: {
        task: 'game',
        game_id: jsPsych.timelineVariable('id'),
        trial_id: function(){return played_rounds;}
    }
};



var human_conf ={
    type: jsPsychHtmlSliderResponse,
    stimulus: instructions.game_play.human_conf,
    labels: ['0%','20%','40%', '60%', '80%', '100%'],
    min: 0,
    max: 100,
    slider_start: 50,
    slider_width: function(){
        return slider_size
    },
    button_label: 'Next >',
    require_movement: true,
    data: {
        task: 'human_conf',
        game_id: jsPsych.timelineVariable('id'),
        nr_reds_shown: jsPsych.timelineVariable('nr_reds_shown'),
        trial_id: function(){return played_rounds;},
        true_prob: function(){ return Math.round(jsPsych.timelineVariable('nr_reds')/jsPsych.timelineVariable('nr_total') *100);}
    },
    on_finish: function(data){
        data.human_conf = data.response;
    }
};

var human_AI_conf = { 
    type: jsPsychHtmlSliderResponse,
    stimulus: function(){
        return instructions.game_play_AI.AI_conf +`<p><br> <span class=\"blue\">${jsPsych.timelineVariable('AI_conf')}%</span><br><br></p>` + instructions.game_play_AI.human_AI_conf;
    },
    labels: ['0%','20%','40%', '60%', '80%', '100%'],
    min: 0,
    max: 100,
    slider_start: function(){
        var human_conf = jsPsych.data.getLastTimelineData().select('human_conf').values.at(-1);
        return human_conf;
    },
    slider_width: function(){
        return slider_size
    },
    button_label: 'Next >',
    require_movement: false,
    data: {
        task: 'human_AI_conf',
        game_id: jsPsych.timelineVariable('id'),
        Ai_conf: jsPsych.timelineVariable('AI_conf'),
        trial_id: function(){return played_rounds;}
    },
    on_finish: function(data){
        data.human_AI_conf = data.response;
    }
};

var initial_decision = {
    type: jsPsychHtmlButtonResponse,
    stimulus: function(){
        return `Based on <span class=\"orange\"> your stated confidence of ${jsPsych.data.getLastTimelineData().select('human_conf').values.at(-1)}\% </span> that the picked card is red, ` + instructions.game_play.decision; 
    },
    choices: ['Black','Red'],
    button_html: ['<button class="black-btn">%choice%</button>','<button class="red-btn">%choice%</button>'],
    data: {
        task: 'decision',
        game_id: jsPsych.timelineVariable('id'),
        trial_id: function(){return played_rounds;}
    },
    on_finish: function(data){
        data.initial_decision = ['Black','Red'].at(data.response);
    }
};

var final_decision = {
    type: jsPsychHtmlButtonResponse,
    stimulus: function(){
        return `Based on <span class=\"orange\"> your stated confidence of ${jsPsych.data.getLastTimelineData().select('human_AI_conf').values.at(-1)}\% </span> that the picked card is red, ` +instructions.game_play_AI.decision;
    },
    choices: ['Black','Red'],
    button_html: ['<button class="black-btn">%choice%</button>','<button class="red-btn">%choice%</button>'],
    data: {
        task: 'decision',
        game_id: jsPsych.timelineVariable('id'),
        trial_id: function(){return played_rounds;}
    },
    on_finish: function(data){
        data.final_decision = ['Black','Red'].at(data.response);
    }
};

var outcome_example = {
    type: jsPsychHtmlButtonResponse,
    stimulus: function(){
        var initial_decision = jsPsych.data.getLastTimelineData().select('initial_decision').values.at(-1);
        var final_decision = jsPsych.data.getLastTimelineData().select('final_decision').values.at(-1);
        return randomDrawn(jsPsych.timelineVariable('cards'), initial_decision, final_decision, example=true);
    },
    choices: ['Next >'],
    data: {
        task: 'outcome_intro',
        game_id: grid_intro.id,
        trial_id: function(){return played_rounds-1;},
	points: function() {return points;}	
    },
    on_finish: function(data){
        var card = data.stimulus;
            if (["hearts","diamonds"].some(v => card.includes(v))) {
                data.outcome =  "Red" ;
            }else if (["clubs","spades"].some(v => card.includes(v))){
                data.outcome =  "Black";
            }
    }
};

var outcome = {
    type: jsPsychHtmlButtonResponse,
    stimulus: function(){
        var initial_decision = jsPsych.data.getLastTimelineData().select('initial_decision').values.at(-1);
        var final_decision = jsPsych.data.getLastTimelineData().select('final_decision').values.at(-1);
        return randomDrawn(jsPsych.timelineVariable('cards'), initial_decision, final_decision);
    },
    choices: ['Next >'],
    data: {
        task: 'outcome',
        game_id: jsPsych.timelineVariable('id'),
        trial_id: function(){return played_rounds-1;},
	    points: function() {return points;}
    },
    on_finish: function(data){
        var card = data.stimulus;
        if (["hearts","diamonds"].some(v => card.includes(v))) {
            data.outcome =  "Red" ;
        }else if (["clubs","spades"].some(v => card.includes(v))){
            data.outcome =  "Black" ;
        }
    }
};

var survey = {
    type: jsPsychSurvey,
    pages: [
      [
        {
          type: 'likert-table',
          prompt: 'State how much you agree with following statement about the AI.',
          name: 'statements',
          statements: instructions.survey[0],
          options: ['Strongly Disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly Agree'],
          required: true
        },
        {
            type: 'multi-choice',
            prompt: 'Choose the statement that best applies to this round.',
            name: 'recap',
            options: instructions.survey[1],
            required: true
          }
      ]
    ],
    button_label_finish: "Next Round >",
    data: {
        task: 'survey',
        game_id: jsPsych.timelineVariable('id'),
        trial_id: function(){return played_rounds-1;},
    },
    on_finish: function(data){
        jsPsych.setProgressBar(data.trial_index/overall_trials);
        var statements = data.response.statements;
        data.statements = statements;
        var recap = data.response.recap;
        data.recap = recap;
    }
  };


function predict_proba(human_conf, ai_conf){

    var delta = alignment_alg[human_conf]["delta"];
    var y_score = ai_conf/100 + Math.random() * delta/(1+delta);
    var bin_edges = alignment_alg[human_conf]["bin_upper_edges"];
    var bin = bin_edges.findIndex(element => element > y_score);

    return Math.round(alignment_alg[human_conf]["mean_pred_values"][bin]);

}

var human_AI_aligned_conf = { 
    type: jsPsychHtmlSliderResponse,
    stimulus: function(){
        var human_conf = jsPsych.data.getLastTimelineData().select('human_conf').values.at(-1);
        const conf_levels = ["very low", "low", "high", "very high","very high"]
        const divider = 25
        var human_conf_level = conf_levels[Math.floor(human_conf/divider)];
        // resolve conf=50 using initial_decision
        var initial_decision = jsPsych.data.getLastTimelineData().select('initial_decision').values.at(-1);
        if (human_conf==50 && initial_decision=="Red"){ human_conf_level = "high"}
        if (human_conf==50 && initial_decision=="Black"){ human_conf_level = "low"}
        console.log(human_conf_level);
        // get entry in AI_aligned with key human_conf_level and AI_conf
        var AI_conf = jsPsych.timelineVariable('AI_conf')
        var AI_aligned_conf = predict_proba(human_conf_level, AI_conf);

        return instructions.game_play_AI.AI_conf +`<p><br> <span class=\"blue\">${AI_aligned_conf}%</span><br><br></p>` + instructions.game_play_AI.human_AI_conf;
    },
    labels: ['0%','20%','40%', '60%', '80%', '100%'],
    min: 0,
    max: 100,
    slider_start: function(){
        var human_conf = jsPsych.data.getLastTimelineData().select('human_conf').values.at(-1);
        return human_conf;
    },
    slider_width: function(){
        return slider_size
    },
    button_label: 'Next >',
    require_movement: false,
    data: {
        task: 'human_AI_conf',
        game_id: jsPsych.timelineVariable('id'),
        Ai_conf: jsPsych.timelineVariable('AI_conf'),
        Ai_calibrated_conf: function(){
            var human_conf = jsPsych.data.getLastTimelineData().select('human_conf').values.at(-1);
            const conf_levels = ["very low", "low", "high", "very high","very high"]
            const divider = 25
            var human_conf_level = conf_levels[Math.floor(human_conf/divider)];
            // resolve conf=50 using initial_decision
            var initial_decision = jsPsych.data.getLastTimelineData().select('initial_decision').values.at(-1);
            if (human_conf==50 && initial_decision=="Red"){ human_conf_level = "high"}
            if (human_conf==50 && initial_decision=="Black"){ human_conf_level = "low"}
            // get entry in AI_aligned with key human_conf_level and AI_conf
            var AI_conf = jsPsych.timelineVariable('AI_conf')
            var AI_aligned_conf = predict_proba(human_conf_level, AI_conf);
            return AI_aligned_conf;
        },
        trial_id: function(){return played_rounds;}
    },
    on_finish: function(data){
        data.human_AI_conf = data.response;
    }
};

var if_level_BP = {
    timeline: [human_AI_aligned_conf],
    conditional_function: function(){
	    if (level_string=="level_BP"){
		    return true;
	    } else {
		    return false;
	    }
    }
};

var if_not_level_BP = {
    timeline: [human_AI_conf],
    conditional_function: function(){
	    if (level_string=="level_BP"){
		    return false;
	    } else {
		    return true;
	    }
    }
};

var start = {
    type: jsPsychHtmlButtonResponse,
    stimulus: "<p> Let's start the game! <br><br> From now on we will count the points in each round. <br> When the game finishes, <span class=\"orange\">each point</span> you have gained translates into a <span class=\"orange\">monetary bonus of 10 cents (£0.08)</span>. <br> Negative or zero points result in no bonus. <br><br> Please, do your best in each round! <br><br></p>",
    choices: ['Start Game >'],
    data: {
        task: 'start'
    },
    on_finish: function(data){
        jsPsych.setProgressBar(data.trial_index/overall_trials);
    } 
}; 

/* Example */
var example = {
    timeline: [ game_pile, human_conf, initial_decision, human_AI_conf, final_decision, outcome_example, survey],
    timeline_variables: [attention_tests.at(3)]
}

/* Training */
var training = {
    timeline: [ game_pile, human_conf, initial_decision, human_AI_conf, final_decision, outcome, survey],
    timeline_variables: attention_tests.slice(1,3)
}

var halfway = Math.round(nr_trials/2);


var game_play_1 = {
    timeline: [ game_pile, human_conf, initial_decision, if_level_BP, if_not_level_BP, final_decision, outcome, survey],
    timeline_variables: games_shuffled.slice(0, halfway) 
}

var game_play_2 = {
    timeline: [ game_pile, human_conf, initial_decision, if_level_BP, if_not_level_BP, final_decision, outcome, survey],
    timeline_variables: games_shuffled.slice(halfway, nr_trials) 
}


/* Attention test */
var attention_test_trial = {
    timeline: [ game_pile, human_conf, initial_decision, human_AI_conf, final_decision, outcome, survey],
    timeline_variables: [attention_tests.at(0)],
    // sample: {
    //     type: 'without-replacement',
    //     size: 1
    // }
    // randomize_order: true
}


var intermission_block = {
    type: jsPsychHtmlButtonResponse,
    stimulus: function(){ return `<p>You are halfway through the game. <br> You have <span class=\"orange\"> earned ${points} point(s) from ${played_rounds} rounds until now</span>.<br><br></p>`;
    },
    choices: ["Next >"],
    data: {
        task: 'intermission'
    },
    on_finish: function(data){
        jsPsych.setProgressBar(data.trial_index/overall_trials);
    }
};

timeline.push( example, start, training, game_play_1, attention_test_trial, intermission_block, game_play_2)


var save_data = {
    type: jsPsychCallFunction,
    async: true,
    func: function(done){
      var xhr = new XMLHttpRequest();
      xhr.open('POST', 'write_data.php');
      xhr.setRequestHeader('Content-Type', 'application/json');
      console.log(jsPsych.data.get().json())
      xhr.onload = function() {
        if(xhr.status == 200){
          var response = JSON.parse(xhr.responseText);
          console.log(response.success);
        }
        done(); // invoking done() causes experiment to progress to next trial.
      };
      xhr.send(jsPsych.data.get().json());
    }
}

var debrief_block = {
    type: jsPsychHtmlButtonResponse,
    stimulus: function(){
        return `<div class=\"content\"> <p>You have completed the game and <span class=\"orange\">earned ${points} point(s) from ${played_rounds} rounds</span>.<br><br></p>
     </div> `;
    },
    choices: ["Next >"],
    data: {
        task: 'debrief'
    },
    on_finish: function(data){
        jsPsych.setProgressBar(data.trial_index/overall_trials);
    }
};

var final_survey = {
    type: jsPsychSurvey,
    pages: [
      [ {
          type: 'html',
          prompt:  `<p>Please answer the following questions about your overall thoughts on the AI during the game.</p> `
        },
        {
          type: 'likert-table',
          prompt: 'State how much you agree with following statements about the AI.',
          name: 'statements',
          statements: instructions.final_survey[0],
          options: ['Strongly Disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly Agree'],
          required: true
        },
        {
            type: 'multi-choice',
            prompt: 'Choose the statement that best applies.',
            name: 'recap',
            options: instructions.final_survey[1],
            required: true
          }
      ]
    ],
    button_label_finish: "Next >",
    data: {
        task: 'final_survey'
    },
    on_finish: function(data){
        jsPsych.setProgressBar(data.trial_index/overall_trials);
        var statements = data.response.statements;
        data.final_statements = statements;
        var recap = data.response.recap;
        data.final_recap = recap;
    }
  };

var demographic_survey = {
    type: jsPsychSurvey,
    pages: [
      [
        {
          type: 'html',
          prompt: 'Please fill in the following demographic information before completing the study:',
        },
        {
            type: 'text',
            prompt: 'What is your age?',
            name: 'age',
            input_type: 'number'
        }, 
        {
            type: 'multi-choice',
            prompt: 'Which gender do you identify with?',
            name: 'gender',
            options: ["Female", "Male", "Non-binary", "Other", "I prefer not to say"],
            required: true
        },
        {
            type: 'multi-choice',
            prompt: 'What is your highest acquired degree?',
            name: 'degree',
            options: ["High School Diploma", "Technical/community college", "Undergraduate degree", "Graduate degree", "Doctorate degree", "Other", "I prefer not to say"],
            required: true
        },
        {
            type: 'multi-choice',
            prompt: 'What subject area does your degree most closely relate to?',
            name: 'subjects',
            options: ["Mathematics and Statistics", "IT and Engineering", "Natural Sciences", "Social Sciences", "Other", "I prefer not to say"],
            required: true
        }, 
      ]
    ],
    button_label_finish: "Next >",
    data: {
        task: 'demographic_survey'
    },
    on_finish: function(data){
        jsPsych.setProgressBar(data.trial_index/overall_trials);
        data.age = data.response.age;
        data.gender = data.response.gender;
        data.degree = data.response.degree;
        data.subjects = data.response.subjects;
    }
  };

timeline.push(debrief_block, final_survey, demographic_survey)
  
var thanks = {
    type: jsPsychHtmlButtonResponse,
    stimulus: function(){
        return `<div class=\"content\">
        <p>Thank you for participating in this study!<br><br> Click "Finish" to be redirected to Prolific. <br><br></p> 
     </div> <div class=\"bottom-link\"> <a href=\"https://imprint.mpi-klsb.mpg.de/sws/hac-experiment.mpi-sws.org\" class=\"my-link\">Imprint</a> | <a href=\"https://data-protection.mpi-klsb.mpg.de/sws/hac-experiment.mpi-sws.org?lang=en\" class=\"my-link\">Data Protection</a> </div>  
        `;
    },
    choices: ["Finish >"],
    data: {
        task: 'thanks'
    },
    // redirect to prolific
    // on_finish: function(){
    //     window.location = completion_URL
    // }
};

var write_metadata = {
    type: jsPsychCallFunction,
    async: true,
    func: function(done){
        jsPsych.data.write({
            subject_id: subject_id,
            study_id: study_id,
            game_batch: game_batch,
            session_id: session_id,
            total_points: points,
	        level_name: level_string
        });
	done();
    }
}

// code used to save data to the server, if needed
// timeline.push(write_metadata, save_data);
timeline.push(thanks);

jsPsych.run(timeline);
