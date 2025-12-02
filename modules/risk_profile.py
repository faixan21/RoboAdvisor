# modules/risk_profile.py

def ask_risk_questions():
    questions = [
        ("How old are you?", "number"),
        ("How stable is your income? (1 = unstable, 5 = very stable)", "scale"),
        ("How long do you want to stay invested? (years)", "number"),
        ("How do you react to market crashes? (1 = panic, 5 = stay calm)", "scale"),
        ("How much investment experience do you have? (1 = none, 5 = expert)", "scale"),
        ("If your portfolio dropped 10%, what would you do? (1 = sell, 5 = buy more)", "scale"),
    ]

    answers = []
    for q, qtype in questions:
        print("\n" + q)
        while True:
            ans = input("> ")
            try:
                ans = float(ans)
                answers.append(ans)
                break
            except:
                print("Please enter a valid number.")

    return answers


def calculate_risk_profile(answers):
    total = sum(answers)

    if total < 15:
        return "Conservative"
    elif total < 22:
        return "Moderate"
    else:
        return "Aggressive"


def get_risk_profile():
    print("\n--- RISK PROFILE TEST ---")
    answers = ask_risk_questions()
    profile = calculate_risk_profile(answers)

    print("\nYour risk profile is:", profile)
    return profile