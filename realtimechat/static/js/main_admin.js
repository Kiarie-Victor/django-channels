const chatRoom = document.querySelector('#room_uuid').textContent.replaceAll('"','')
let chatSocket = null

const anchorTag = document.getElementById('connect')
const chatLogElement = document.querySelector('#chat_log')
const chatInputElement = document.querySelector('#chat_message_input')

const chatSubmitElement = document.querySelector('#chat_message_submit')

function scrollToBottom (){
    chatLogElement.scrollTop = chatLogElement.scrollHeight
}

function sendMessage () {
    console.log(document.querySelector('#user_name').textContent.replaceAll('"', ''))
    chatSocket.send(JSON.stringify({
        'type':'message',
        'message': chatInputElement.value,
        'name': document.querySelector('#user_name').textContent.replaceAll('"', ''),
        'agent': document.querySelector('#user_id').textContent.replaceAll('"', '')
}))
chatInputElement.value = ''
}

const onChatMessage = (data) => {
    if (data.type == 'chat_message'){
        let tmpInfo = document.querySelector('.tmp-info')

        if(tmpInfo){
            tmpInfo.remove()
        }

        if(data.agent){
            chatLogElement.innerHTML += `
            <div class = "flex w-full mt-2 space-x-3 max-w-md ml-auto justify-end">
            <div class="flex-shrink-0 h-10 w-10 rounded-full bg-gray-300 text-center pt-2">${data.initials}</div>
                    <div>
                        <div class = "bg-gray-300 p-3 rounded-l-lg">
                            <p class = "text-sm"> ${data.message}</p>
                        </div>

                            <span class = "text-xs text-gray-500 leading-none">${data.created_at} ago</span>
                    </div>

                    
            </div>`

        }
        else{
            chatLogElement.innerHTML += `
            <div class = "flex w-full mt-2 space-x-3 max-w-md ml-auto justify-end">
                        
                    <div>
                        <div class = "bg-blue-300 p-3 rounded-l-lg">
                            <p class = "text-sm"> ${data.message}</p>
                        </div>

                            <span class = "text-xs text-gray-500 leading-none">${data.created_at} ago</span>
                    </div>

                    <div class="flex-shrink-0 h-10 w-10 rounded-full bg-gray-300 text-center pt-2">${data.initials}</div>
            </div>`
        }
    } else if (data.type == 'writing_active'){
        if(!data.agent){
            let tmpInfo = document.querySelector('.tmp-info')

            if(tmpInfo){
                tmpInfo.remove()
            }

            chatLogElement.innerHTML += `
            <div class = "tmp-info flex w-full mt-2 space-x-3 max-w-md ml-auto justify-end">
            <div class="flex-shrink-0 h-10 w-10 rounded-full bg-gray-300 text-center pt-2">${data.initials}</div>
                    <div>
                        <div class = "bg-gray-300 p-3 rounded-l-lg">
                            <p class = "text-sm">The user is typing </p>
                        </div>
                    </div>

                    
            </div>`

        }}

    scrollToBottom()
}


chatSocket= new WebSocket(`ws://${window.location.host}/ws/chat/${chatRoom}/`)
console.log('connecting')

chatSocket.onmessage = (e) => {
    const data = JSON.stringify(e.data)
    onChatMessage(data)
}

chatSocket.onopen = (e) => {
    scrollToBottom()
    console.log('on open')
}

chatSocket.onclose = (e) => {
    console.log('closed unexpectedly')
}


chatSubmitElement.onclick = (e) => {
    sendMessage()

    return false
}

chatInputElement.onkeyup = function (e) {
    if(e.keyCode == 13){
        sendMessage()
    }

}

chatInputElement.onfocus = function(e){
    chatSocket.send(JSON.stringify({
        'type':'update',
        'message': 'writing_active',
        'name': document.querySelector('#user_name').textContent.replaceAll('"', ''),
        'agent': document.querySelector('#user_id').textContent.replaceAll('"', '')
}))

}
