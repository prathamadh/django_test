from pyngrok import ngrok
public_url = ngrok.connect(8000)

print(f"Public URL: {public_url}")

while True:
    user_input = input("Type 'exit' to quit: ")
    if user_input.lower() == 'exit':
        print("Exiting the loop.")
        break
    print(f"You typed: {user_input}")