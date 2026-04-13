// -----------------------------------------------------------------------
// Friends.jsx
// friends interface for Hooked (in progress)
// Authors: Eleanor Liu
// -----------------------------------------------------------------------

import {useCallback, useEffect, useState} from 'react'
import { useNavigate } from 'react-router-dom'
import './index.css'

function Profile(){

    const navigate = useNavigate()
    const [friendUsername, setFriendUsername] = useState("")
    const [user, setUser] = useState(null)

    function handleBackButton() {
        console.log("back button clicked, go back to sw9pe page")
        navigate(-1)
    }

    // obtain the credentials from cookie
    // src: https://dev.to/velcruza/how-to-display-different-components-based-on-user-authentication-8o5
    useEffect(() => {
        fetch("http://localhost:5000/auth/user", { credentials: "include" })
            .then(res => res.json())
            .then(data => setUser(data))
    }, [])

    return (
        <div className='screen-style4'>
        

        <div className='card'>
            <div className='card-header'>
                {user && <p style={{ color: '#debff7', fontWeight: 'bold', cursor: 'pointer' }} 
                onClick={() => navigate('/profile')}>Welcome, {user.name}!</p>}
            </div>
            <h1>My Profile</h1>
            <div className='small-header'>
                <h3 style={{ textAlign: 'left' , padding: '5px'}}>My Top Liked Songs</h3>
            </div>

            <div className='small-header'>
                <h3 style={{ textAlign: 'left' , padding: '5px'}}>My Friends</h3>

                <button className='add-btn' onClick={() => navigate('/friends')}>
                    +
                </button>
            </div>
            
                

            <button className = 'back-btn' onClick={handleBackButton}>
            Back
            </button>

        </div>


        </div>
    );
}

// -------------------- EXPORT --------------------
export default Profile