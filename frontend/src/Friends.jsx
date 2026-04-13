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
    const [likedSongs, setLikedSongs] = useState([]);

    function handleBackButton() {
        console.log("back button clicked, go back to sw9pe page")
        navigate(-1)
    }

    return (
        <div className='screen-style1'>
            <div className='card'>

            <div className='card-header'>
                <h1>Friends</h1>

                <button className = 'back-btn' onClick={handleBackButton}>
                    Back
                </button>
            </div>
                    
            <input
                type="text"
                value={friendUsername}
                onChange={(e) => setFriendUsername(e.target.value)}
                placeholder="Search Username"
                className = 'input-box-3'
            />


            </div>
        </div>
    );
}

// -------------------- EXPORT --------------------
export default Friends