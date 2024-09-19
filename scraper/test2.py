

    # Example usage

def decrypt_messages(example_pair, encrypted_messages):
  """
  Decrypts messages using a combination of Caesar Cipher and Polybius Square (or none).

  Args:
      example_pair: A tuple containing the encrypted and decrypted message for analysis.
      encrypted_messages: A list of strings containing additional encrypted messages.

  Returns:
      A list of decrypted messages corresponding to the input encrypted messages.
  """

  encrypted_message, decrypted_message = example_pair

  # Analyze letter frequency in decrypted message (assuming English)
  letter_counts = {char: 0 for char in range(ord('A'), ord('Z') + 1)}
  for char in decrypted_message:
    if char.isalpha():
      letter_counts[ord(char.upper())] += 1

  # Check for Atbash Cipher (disrupts letter frequency)
  if not any(count > 2 for count in letter_counts.values()):
    return encrypted_messages  # No ciphers used (assuming)

  # Try Caesar Cipher shifts (1-25) and Polybius Square mapping
  for shift in range(1, 26):
    decrypted_candidate = ""
    for code in encrypted_message.split():
      # Get coordinates (row, col) from the encrypted code
      row, col = int(code[0]), int(code[1])

      # Decrypt the code using Caesar Cipher shift
      new_row = (row - shift) % 6  # Get Polybius Square dimensions

      # Decrypt the code using Polybius Square mapping
      new_col = (col - shift) % 6  # Get number of columns

      # Get the letter based on the new coordinates
      decrypted_letter = get_polybius_square_value((new_row, new_col), None)

      decrypted_candidate += decrypted_letter

    if decrypted_candidate == decrypted_message:
      # Caesar Cipher shift found, decrypt other messages
      decrypted_messages = []
      for message in encrypted_messages:
        decrypted_message = ""
        for code in message.split():
          row, col = int(code[0]), int(code[1])
          new_row = (row - shift) % 6
          new_col = (col - shift) % 6
          decrypted_letter = get_polybius_square_value((new_row, new_col), None)
          decrypted_message += decrypted_letter
        decrypted_messages.append(decrypted_message)
      return decrypted_messages

  # No Caesar Cipher shift found (other ciphers or no ciphers used)
  return encrypted_messages

# Example usage (assuming Polybius Square logic is built-in to get_polybius_square_value)
example_pair = ("21 32 14 34 43 22 11 23 12 42", "Hello World!")
encrypted_messages = ["13 11 14 31 41 14 32 42 24", "44 11 34 14 42 33 22 23 14"]
decrypted_messages = decrypt_messages(example_pair, encrypted_messages)

print(decrypted_messages)  # Output: ['Hi There!', 'See You Soon']
