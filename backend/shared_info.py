shared_info = {
    "x" : 18,
    'y' : 2
}

currency = "£"
fixed_payment = "2.5"

# Set question text
experiment_text = {
    "welcome" : "Welcome to the experiment!",
    "instructions" : f"""
    You will be presented with a series of questions.
    In each question, you will be asked to choose between receiving a sure amount of money or participating in a lottery.
    To make your choice, select the option you prefer and then confirm your choice.

    There is no right or wrong answer: we are simply interested in your preferences.

    For your participantion in the experiment, you will receive a fixed payment of {currency}{fixed_payment}.
    In addition, you have a chance to win a bonus payment up to {currency}{shared_info['x']} based on your choices.
    One in ten participants will be randomly selected for bonus payment.
    If you are selected, one of the choices made in the experiment will be randomly selected and the associated win will be added to your payment.
    If the selected choice is a lottery, the bonus payment is determined by simulating the outcome of the lottery.

    You will now be presented a practice question, to familiarize yourself with the task. 
    Press the button below to proceed to the practice question.
    """,
    "amount_currency" : currency,
    "sentence_string" : "Question {}:\nWhich of the following options do you prefer?",
    "sentence_sure" : "Receiving {} for sure.",
    "sentence_lottery" : "A lottery where you can either receive {} with {} probability, or receive {} otherwise.",
    "final_message" : "The experiment is over, thank you for your help!"
}
