// -----------------------------------------------------------------------
// Friends.jsx
// friends interface for Hooked (in progress)
// Authors: Eleanor Liu
// -----------------------------------------------------------------------

import {useCallback, useEffect, useState} from 'react'
import { useNavigate } from 'react-router-dom'
import './index.css'

function Friends(){

    const navigate = useNavigate()
    const [friendUsername, setFriendUsername] = useState("")

    function handleBackButton() {
        console.log("back button clicked, go back to sw9pe page")
        navigate('/swipe')
    }

    return (
        <div className='screen-style1'>
            <div className='card'>

            <h1>Friends</h1>
            <input
                type="text"
                value={friendUsername}
                onChange={(e) => setFriendUsername(e.target.value)}
                placeholder="Search Friend Username"
                className = 'input-box-1'
            />

            <button className = 'btn-1' onClick={handleBackButton}>
                Back
            </button>
            </div>
        </div>
    );
}

// -------------------- EXPORT --------------------
export default Friends