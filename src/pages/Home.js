import { useState } from "react"
import { useNavigate } from "react-router-dom"
import supabase from "../config/supabaseClient"

const Create = () => {
  const navigate = useNavigate()

  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [phno, setPhno] = useState('')
  const [formError, setFormError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!name || !email || !phno) {
      setFormError('Please fill in all the fields correctly.')
      return
    }

    const { data, error } = await supabase
      .from('User_Profile')
      .insert([{ name, email, phno }])

    if (error) {
      console.log(error)
      setFormError('Error creating user profile.')
    }
    else{
      alert("Profile Built Successfully")
    }
    if (data) {
      console.log(data)
      setFormError(null)
      navigate('/')
    }
  }

  return (
    <div className="page create">
      <form onSubmit={handleSubmit}>
        <label htmlFor="name">Name:</label>
        <input 
          type="text" 
          id="name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />

        <label htmlFor="email">Email:</label>
        <input 
          type="email" 
          id="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <label htmlFor="phno">Phone Number:</label>
        <input 
          type="tel"
          id="phno"
          value={phno}
          onChange={(e) => setPhno(e.target.value)}
        />

        <button>Create User Profile</button>

        {formError && <p className="error">{formError}</p>}
      </form>
    </div>
  )
}

export default Create
