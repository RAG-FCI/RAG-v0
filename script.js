document.addEventListener('DOMContentLoaded', function () {
    const input = document.getElementById('input');
    const output = document.getElementById('output');

    if (!input || !output) {
        console.error('Elementos de input ou output não encontrados.');
        return;
    }

    input.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
            const command = input.value;
            if (command.trim()) {
                executeCommand(command);
            }
            input.value = ''; // Clear input after command execution
        }
    });

    function executeCommand(command) {
        const commandOutput = document.createElement('div');
        commandOutput.textContent = `user@simulado:~$ ${command}`;
        output.appendChild(commandOutput);

        if (command.startsWith('bruno')){
            const prompt = command.slice(5);
            processPrompt(prompt); //Process the prompt with LLM
        }
        else if (command === 'help') {
            const result = document.createElement('div');
            result.textContent = 'Comandos disponíveis: help, bruno, clear';
            output.appendChild(result);
        } 
        else if (command === 'clear') {
            output.innerHTML = ''; // Clear the output area
            return;
        } else {
            const result = document.createElement('div');
            result.textContent = `Comando não encontrado: ${command}`;
            output.appendChild(result);
        }
        
        output.scrollTop = output.scrollHeight; // Scroll to the bottom
    }
    function processPrompt(prompt) {
        // Simular uma requisição ao modelo LLM
        fetch('http://127.0.0.1:5000/interpretar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ prompt: prompt })
        })
        .then(response => response.json())
        .then(data => {
            const result = document.createElement('div');
            result.textContent = data.resposta; // A resposta do modelo LLM
            output.appendChild(result);
            output.scrollTop = output.scrollHeight; // Scroll to the bottom
        })
        .catch(error => {
            const result = document.createElement('div');
            result.textContent = 'Erro ao processar o prompt: ' + error;
            output.appendChild(result);
            output.scrollTop = output.scrollHeight; // Scroll to the bottom
        });
    }
});