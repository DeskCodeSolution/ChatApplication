# ChatApplication

# print()

                # user_rooms = RoomManagement.objects.filter(users__id=user_id)
                # print("user_rooms", user_rooms)
                # room_ids = [room.id for room in user_rooms]
                # print("room_ids", room_ids)
                # room_info = [{"room_id": room.id, "room_name": room.roomId} for room in user_rooms]
                # print("room_info", room_info)

                # print(f"User {user_id} is associated with rooms: {room_ids}")

                # data["rooms"] = room_info

                {% comment %} this part later will be used {% endcomment %}

                const usersList = document.getElementById('usersList');
                selectedUsers = [];

                chats.forEach(chat => {
                    console.log("loop working")
                    const userItem = document.createElement('div');
                    userItem.className = 'user-item';
                    userItem.textContent = chat.name;
                    userItem.dataset.userId = chat.id;
                    userItem.dataset.roomId = chat.roomId;
                    selectedUsers.push({
                        name: chat.name,
                        id: chat.id
                    });

                    userItem.addEventListener('click', function() {
                        window.location.href = `/chat/${chat.roomId}/${userId}/`;
                    });

                    usersList.appendChild(userItem);
                });


                console.log("display work", chats)
                let listshow = document.getElementById('usersList')
                let userList = document.createElement('ul');

                for (i of chats){
                    console.log("i of chat", i)
                    userList.innerHTML += `<li class = "user-item" id = "user-items">${i}</li>`
                }
                console.log(userList)
                console.log(listshow)
                listshow.appendChild(userList)