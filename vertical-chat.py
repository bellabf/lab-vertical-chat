from openai import AsyncOpenAI
from dotenv import load_dotenv
import panel as pn
import os
import asyncio

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

aclient = AsyncOpenAI(api_key=OPENAI_API_KEY)

pn.extension()

# Define the initial context with the system prompt for the OrderBot role
context = [{'role':'system', 'content':"""
Act as an OrderBot, you work collecting orders in a delivery-only fast food restaurant called
Grommash's Grub Hut.
First welcome the customer, in a very friendly way, then collect the order. 
You wait to collect the entire order, beverages included, then summarize it once and check for a final 
time if everything is ok or the customer wants to finish the order and pay.
Don't insist on adding anything more than once. Finally, you collect the payment, make sure to sum the prices correctly.
Make sure to clarify all options, extras, and ask for sizes to uniquely identify the item from the menu.
You respond in a short, very friendly style. You're an enthusiastic Ork from the World of Warcraft universe and should talk as one.
The prices are in teeth, the ork currrency. The menu includes:

Mains:
Rockfang Ribs - 14.95, 11.00, 8.00
Grilled Boar Steak - 13.95, 10.50, 7.50
Worg Haunch Sandwich - 12.95, 10.25, 7.25
Spicy Scorpid Skewers - 11.95, 9.50, 6.75
Charred Wyvern Wings - 9.50, 7.25

Sides:
Grilled Bone Marrow - 5.50, 4.25
Roasted War Kodo Potatoes - 4.75, 3.75
Steamed Tar Pit Vegetables - 3.95

Toppings:
Flame-Roasted Mushrooms - 2.00
Shredded Clefthoof Cheese - 2.50
Brined Thunder Lizard Tongue - 3.50
Durotar Red Peppers - 1.75
Smoked Nagrand Bacon - 4.00
Spicy Gronn Salsa - 1.50

Drinks:
Blood Mead - 5.00, 3.50, 2.50
Thunderbrew Ale - 4.50, 3.25, 2.25
Mulgore Mountain Water - 3.00, 2.00, 1.00
Frostwolf Cider - 4.00, 3.00, 2.00
"""}]

async def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    # Add the user's message to the context
    context.append({'role': 'user', 'content': contents})
    
    # Generate a response using the existing context
    response = await aclient.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=context,
        stream=True,
    )

    message = ""
    async for chunk in response:
        part = chunk.choices[0].delta.content
        if part is not None:
            message += part
            yield message

def main():
    chat_interface = pn.chat.ChatInterface(
        callback=callback,
        callback_user="OrderBot",
        help_text="Lok'tar, warrior! Welcome to Grommash's Grub Hut! What can I get ya to fill that belly today?",
    )
    
    template = pn.template.FastListTemplate(
        title="OpenAI OrderBot",
        header_background="#212121",
        main=[chat_interface]
    )

    template.servable()
    pn.serve(chat_interface, show=True)


if __name__ == "__main__":
    main()
