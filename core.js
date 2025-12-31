/* 
   CHIMERA CORE SYSTEM LOGIC
   Version: 1.0.0
*/

// --- MOCK DATABASE (ตัวอย่างข้อมูล) ---
const MEMORY_DB = [
    {
        date: "2021-12-28",
        logs: [
            { id: "M001", sender: "USR_00", type: "text", content: "System check... is anyone there?" },
            { id: "M002", sender: "ENT_01", type: "text", content: "Connection established. I am here." },
            { id: "M003", sender: "USR_00", type: "text", content: "Good. Let's begin the archive." }
        ]
    },
    {
        date: "2022-01-15",
        logs: [
            { id: "M004", sender: "ENT_01", type: "image", content: "Visual Data [Encrypted]", meta: "sketch_concept" },
            { id: "M005", sender: "USR_00", type: "text", content: "This structure... it's beautiful." }
        ]
    }
];

const System = {
    init: function() {
        document.getElementById('start-screen').style.display = 'none';
        document.getElementById('main-interface').style.display = 'flex';
        UI.loadTimeline();
        // Load first entry by default
        if(MEMORY_DB.length > 0) UI.loadChat(0);
    }
};

const UI = {
    toggleSidebar: function() {
        document.getElementById('sidebar').classList.toggle('active');
    },

    loadTimeline: function() {
        const list = document.getElementById('timeline-list');
        list.innerHTML = '';
        MEMORY_DB.forEach((entry, index) => {
            let el = document.createElement('div');
            el.className = 'date-item';
            el.innerHTML = `> LOG: ${entry.date}`;
            el.onclick = () => {
                this.loadChat(index);
                this.toggleSidebar(); // Auto close on mobile
            };
            list.appendChild(el);
        });
    },

    loadChat: function(index) {
        const container = document.getElementById('chat-container');
        container.innerHTML = ''; // Clear current
        
        // Add Date Header
        let header = document.createElement('div');
        header.className = 'system-msg';
        header.innerText = `// LOADED SEQUENCE: ${MEMORY_DB[index].date} //`;
        container.appendChild(header);

        MEMORY_DB[index].logs.forEach(msg => {
            let row = document.createElement('div');
            let role = msg.sender === 'USR_00' ? 'msg-usr' : 'msg-ent';
            row.className = `msg-row ${role}`;

            let bubble = document.createElement('div');
            bubble.className = 'bubble';

            let time = document.createElement('span');
            time.className = 'timestamp';
            time.innerText = `[ID: ${msg.id}] :: ${msg.sender}`;
            
            let content = document.createElement('div');
            if (msg.type === 'image') {
                content.innerHTML = `<div style="border:1px dashed #444; padding:20px; text-align:center; color:#666;">
                    [ VISUAL SYNTHESIS: ${msg.meta} ]<br>
                    &lt;svg_renderer_placeholder&gt;
                </div>`;
            } else {
                content.innerText = msg.content;
            }

            bubble.appendChild(time);
            bubble.appendChild(content);
            row.appendChild(bubble);
            container.appendChild(row);
        });
        
        // Scroll to bottom
        container.scrollTop = container.scrollHeight;
    }
};
