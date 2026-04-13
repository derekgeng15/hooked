// -----------------------------------------------------------------------
// WelcomePage.jsx
// Swipe interface for Hooked (in progress)
// Authors: Eleanor Liu
// Contributors:  Lucille Rizo Patron
// -----------------------------------------------------------------------

import React from 'react'
import {useCallback, useEffect, useState} from 'react'
import { useNavigate} from 'react-router-dom'
import './index.css'

//circles
import Circle from "./AnimatedCircle.jsx"
import musicNote1 from './musical-note-1.png'
import musicNote2 from './musical-note-2.png'

function SignUp(){

    // this makes it go from one screen to another
    const navigate = useNavigate()
    const [username, setUsername] = useState("")
    const [password, setPassword] = useState("")

    const handleKeyPress = useCallback((e) => {
        if (e.key === ' ' || e.code === "Space") {
            console.log('Space pressed')
            navigate('/seedprefs')
        }
    }, [navigate])

    useEffect(() => { 
        window.addEventListener('keydown', handleKeyPress)
        return () => window.removeEventListener('keydown', handleKeyPress)
    }, [handleKeyPress])

    return(
        <div className='screen-style6'> 
            Create an Account <br />

            <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Username"
                className = 'input-box-1'
            />

            <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
                className = 'input-box-1'
            />
            
            <table>
            <button className = 'btn-1' onClick = { () => {
                console.log("back button clicked! lets migrate to welcome page")
                navigate('/')
            }}> 
                Back 
            </button>

            <button className = 'btn-1' onClick = {() => {
                navigate('/seedprefs')
                console.log("acc created... we are going to seed our preferences")}
                }> 
                Create!
            </button>
            </table>

            <Circle image={musicNote1} alpha={0.015}/>            
            <Circle image={musicNote1} alpha={0.015}/>
            <Circle image={musicNote1} alpha={0.015}/>
            <Circle image={musicNote2} alpha={0.015}/>
            <Circle image={musicNote2} alpha={0.015}/>
            <Circle image={musicNote2} alpha={0.015}/>
            
        </div>
    )
}


// --------------------------------- EXPORT --------------------------------

export default SignUp