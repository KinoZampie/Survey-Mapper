from flask import Flask, render_template, url_for, request, redirect
import uuid, json, os, random

'''
8values
Economic   Diplomatic   Civil       Societal
equality   nation       liberty     tradition   + positive
market     world        authority   progress    - negative
'''


# Initalization starts everything at neutrality
def initialization():
    global economic, diplomatic, civil, societal, neutral, mininum, maximum
    # In a range of 0-100, 50 is neutral.
    economic = 50
    diplomatic = 50
    civil = 50
    societal = 50
    # Mininum is strongly disagree, while maximum is strongly agree.
    mininum = 1
    maximum = 7
    neutral = (mininum + maximum) / 2

#This function debugs the values for some variables.
def debug():
    global economic, diplomatic, civil, societal
    print("Economic: "+str(economic))
    print("Diplomatic: "+str(diplomatic))
    print("Civil: "+str(civil))
    print("Societal: "+str(societal))

# This function asks questions and gives points to appropiate categories
def question_asker(issue, answer, weight=1):
    global economic, diplomatic, civil, societal, neutral, mininum, maximum
    # The points are calculated depending on how strong the position is.
    if answer<neutral:
        points=-pow(2, abs(answer-neutral)-1)*weight
    elif answer==neutral:
        points=0
    else:
        points=pow(2, abs(answer-neutral)-1)*weight
    '''Issues:
       1. Economic
       2. Diplomatic
       3. Civil
       4. Societal'''
    if issue == "equality":
        economic += points
    if issue == "market":
        economic-=points
    if issue == "nation":
        diplomatic+=points
    if issue == "world":
        diplomatic-=points
    if issue == "liberty":
        civil+=points
    if issue == "authority":
        civil-=points
    if issue == "tradition":
        societal+=points
    if issue == "progress":
        societal-=points
    #The values for economic, diplomatic, civil, and societal are clamped.
    economic=clamp(economic)
    diplomatic=clamp(diplomatic)
    civil=clamp(civil)
    societal=clamp(societal)
    #This function will be used to find the values of economic, diplomatic, civil, and societal.
    # debug()

#This function clamps values to be within a range.
def clamp(val, min=0, max=100):
    if val<min:
        return min
    elif val>max:
        return max
    else:
        return val


def user_creation(fname,lname,city,state,country):
    user_uuid = str(uuid.uuid4().hex)
    user_data = {user_uuid:{
        "user_data":{
            "fname":fname,
            "lname":lname,
            "city":city,
            "state":state,
            "country":country
        },
        "current_question":0,
        "question_data":[

        ],
        "results":{
            "Economic":None,
            "Diplomatic":None,
            "Civil":None,
            "Societal":None
        }
    }
    }
    randomized_questions = list(questions["question_list"])
    random.shuffle(randomized_questions)
    for question in randomized_questions:
        question_none = list(question)
        question_none.append(None)
        user_data[user_uuid]["question_data"].append(question_none)
    with open('users/{}.json'.format(user_uuid), "w") as f:
        f.write(json.dumps(user_data,indent=2))

    return user_uuid

app = Flask(__name__)

with open('questions.json') as f:
    questions = json.load(f)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/userinfo", methods=["GET","POST"])
def userinfo():
    if request.method == "POST":
        if request.form.get('fname') == "" or request.form.get('lname') == "" or request.form.get('city') == "" or request.form.get('state') == "" or request.form.get('country') == "":
            return "Invalid Response (check for empty values)"
        else:
            user_uuid = user_creation(request.form.get('fname'),request.form.get('lname'),request.form.get('city'),request.form.get('state'),request.form.get('country'))
            return redirect(url_for("survey",user_id=user_uuid))
    return render_template("userinfo.html")


@app.route("/survey/<user_id>", methods=["GET","POST"])
def survey(user_id):
    if request.method == "POST":
        if request.form.get("question") == None:
            return redirect(url_for("survey",user_id=user_id))
        else:
            question_response = int(request.form.get("question"))
            with open('users/{}.json'.format(user_id)) as f:
                user_data = json.load(f)
            current_question = user_data[user_id]["current_question"]
            user_data[user_id]["current_question"] = user_data[user_id]["current_question"]+1
            user_data[user_id]["question_data"][current_question][2] = (question_response)
            current_question_number = user_data[user_id]["current_question"]
            with open('users/{}.json'.format(user_id), "w") as f:
                f.write(json.dumps(user_data,indent=2))
            if current_question_number == 31:
                initialization()
                with open('users/{}.json'.format(user_id)) as f:
                    user_data = json.load(f)
                for question in user_data[user_id]["question_data"]:
                    question_asker(question[1],question[2])
                user_data[user_id]["results"]["Economic"] = economic
                user_data[user_id]["results"]["Diplomatic"] = diplomatic
                user_data[user_id]["results"]["Civil"] = civil
                user_data[user_id]["results"]["Societal"] = societal
                with open('users/{}.json'.format(user_id), "w") as f:
                    f.write(json.dumps(user_data,indent=2))
                with open('completed_users.txt', "a") as f:
                    f.write(user_id)
                return redirect(url_for("user_results",user_id=user_id))
            else:
                return redirect(url_for("survey",user_id=user_id))
    with open('users/{}.json'.format(user_id)) as f:
        user_data = json.load(f)
    current_question_number = int(user_data[user_id]["current_question"])
    if current_question_number == 31:
        return redirect(url_for("user_results",user_id=user_id))
    current_question = user_data[user_id]["question_data"][int(user_data[user_id]["current_question"])][0]
    return render_template("survey.html", question=current_question,question_number= current_question_number)

@app.route("/results")
def results():
    with open('completed_users.txt') as f:
        users = f.read().splitlines()
    return render_template("results.html",users = users)

@app.route("/results/<user_id>", methods=["GET","POST"])
def user_results(user_id):
    with open('users/{}.json'.format(user_id)) as f:
        user_data = json.load(f)
    fname = user_data[user_id]["user_data"]["fname"]
    lname = user_data[user_id]["user_data"]["lname"]
    u_economic = user_data[user_id]["results"]["Economic"]
    u_diplomatic = user_data[user_id]["results"]["Diplomatic"]
    u_civil = user_data[user_id]["results"]["Civil"]
    u_societal = user_data[user_id]["results"]["Societal"]
    city = user_data[user_id]["user_data"]["city"]
    state = user_data[user_id]["user_data"]["state"]
    country = user_data[user_id]["user_data"]["country"]
    return render_template("user_results.html",fname=fname,lname=lname, economic=u_economic, diplomatic=u_diplomatic, civil=u_civil, societal=u_societal, city=city, state=state, country=country)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=80)
