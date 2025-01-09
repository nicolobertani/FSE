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
    In each question, you will choose between receiving a fixed amount of money or participating in a lottery.
    To make your choice, simply select the option you prefer on the screen and then confirm your choice.
    Please read the options carefully before making your choice.

    There are no right or wrong answers: we are only interested in your preferences.

    For participating in this experiment, you will receive a fixed payment of {currency}{fixed_payment}.
    Additionally, you have a chance to win a bonus payment of up to {currency}{shared_info['x']}, depending on your choices.
    One in ten participants will be randomly selected for the bonus payment.
    If you are selected, one of your choices from the experiment will be randomly picked, and the associated reward will be added to your payment.
    If the chosen reward is a lottery, the bonus payment will be determined by simulating the outcome of that lottery.
    
    You will now be presented with a practice question to help you become familiar with the task.
    Press the button below to proceed to the practice question.
    """,
    "instructions_reminder" : f"""
    The previous question was just for practice.
    The experiment will now start.
    
    All choices you will make from now could be selected to be added to your final payment."
    """,
    "amount_currency" : currency,
    "sentence_string" : "Question {}:\nWhich of the following options do you prefer?",
    "sentence_sure" : "Receiving {} for sure.",
    # "sentence_lottery" : "A lottery where you can either receive {} with {} probability, or receive {} otherwise.",
    # "sentence_lottery" : "A lottery that will pay:\n\n{} with {} probability,\nor\n{} with {} probability.",
    "sentence_lottery" : "A lottery where you can either receive:\n\n{} with {} probability,\nor\n{} with {} probability.",
    "confirm" : "I confirm my choice.",
    "final_message" : "The experiment is over, thank you for your help!"
}
