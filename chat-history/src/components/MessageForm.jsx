import { useState } from "react";
import {
  Input,
  Stack,
  IconButton,
  useToast,
  Box,
  Container,
} from "@chakra-ui/react";
import { BiSend } from "react-icons/bi";
import { useAppContext } from "../context/appContext";

export default function MessageForm() {
  const { supabase, username, country, auth } = useAppContext();
  const [message, setMessage] = useState("");
  const [data, setData] = useState([]);
  const [error, setError] = useState(null);
  const toast = useToast();
  const [isSending, setIsSending] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSending(true);
    if (!message) return;

    setMessage("");

    try {
      const userInput = message; // Replace with input from user input text field
      console.log(userInput);
      const response = await axios.get(`http://127.0.0.1:5001/api/getChat?prompt=${userInput}`, {
        headers: {
          'Content-Type':'application/json'
        },
      });

      console.log(response.data);
      setData(response.data);
    } catch (error) {
      setError(error);
    }
    finally {
      setData("Please check the console.")
    }

    try {
      const { err1 } = await supabase.from("messages").insert([
        {
          text: message,
          username,
          country,
          is_authenticated: auth.user() ? true : false,
        },
      ]);

      const { err2 } = await supabase.from("messages").insert([
        {
          text: data,
          username: "bot",
          country,
          is_authenticated: auth.user() ? true : false,
        },
      ]);

      if (err1) {
        console.error(err1.message);
        toast({
          title: "Error sending",
          description: err1.message,
          status: "error",
          duration: 9000,
          isClosable: true,
        });
        return;
      }
      if (err2) {
        console.error(err2.message);
        toast({
          title: "Error sending",
          description: err2.message,
          status: "error",
          duration: 9000,
          isClosable: true,
        });
        return;
      }

      console.log("Sucsessfully sent!");
    } catch (err) {
      console.log("error sending message:", err);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <Box py="10px" pt="15px" bg="gray.100">
      <Container maxW="600px">
        <form onSubmit={handleSubmit} autoComplete="off">
          <Stack direction="row">
            <Input
              name="message"
              placeholder="Enter a message"
              onChange={(e) => setMessage(e.target.value)}
              value={message}
              bg="white"
              border="none"
              autoFocus
              maxLength="500"
            />
            <IconButton
              // variant="outline"
              colorScheme="teal"
              aria-label="Send"
              fontSize="20px"
              icon={<BiSend />}
              type="submit"
              disabled={!message}
              isLoading={isSending}
            />
          </Stack>
        </form>
        {/* <Box fontSize="10px" mt="1">
          Warning: do not share any sensitive information, it's a public chat
          room 🙂
        </Box> */}
      </Container>
    </Box>
  );
}
