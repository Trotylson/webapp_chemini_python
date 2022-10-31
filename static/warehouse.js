
main_headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJEYW1pYW4ifQ.49JmaHCvE7bePDuEylskD344AAULyLAB9FPf8hRwHTM'
};


$('#editbtn1').click(function() {
    quantity = $('#move').val();
    item_id = $('#item_id').val();

    data = {
        "quantity":quantity,
        "item_id":item_id
    };

    fetch("/chemini-api/item-update-stack",{
    method: 'PUT',
    headers: main_headers,
    body: JSON.stringify(data)})
    .then(response => response.json())
    .then(result => {
        console.log(JSON.stringify(result))
        
        var server_code = JSON.stringify(result['code'])
        var server_response = JSON.stringify(result['response'])
        if (server_code == 200) {
            alert("SUKCES!\nPomyślnie zmieniono stan magazynowy!")
            location.replace("/warehouse");}
        else if(server_code == 201) {
            alert("BŁĄD!\nNie można zdjąć ze stanu więcej towaru niż jest na magazynie!")}
        else if(server_code == 401) {
            alert("BŁĄD!\nKomunikat serwera: " + server_response)}
        else if(server_code == 500) {
            alert("BŁĄD!\nKomunikat serwera: " + server_response)}
        else {
            alert("BŁĄD NIEOKREŚLONY!\nBrak uwzględnionego kodu.\nZakres uwzględnionych błędów (200, 401, 500)")}
    });
});

       

$('#editbtn2').click(function() {
    item_id = $('#item_id').val();
    item_name = $('#name').val();
    manufacturer = $('#manufacturer').val();
    reference = $('#reference').val();
    stack_min = $('#stack_min').val();
    buy = $('#buy').val();
    sell = $('#sell').val();
    description = $('#description').val();
    code = $('#code').val();
    used = document.getElementById("isused").checked;

    data = {
        "item_id": item_id,
        "item_name": item_name,
        "manufacturer": manufacturer,
        "reference": reference,
        "stack_min": stack_min,
        "buy": buy,
        "sell": sell,
        "description": description,
        "code": code,
        "used": used
    };

    console.log(data)

    fetch("/chemini-api/item-update-all",{
    method: 'PUT',
    headers: main_headers,
    body: JSON.stringify(data)})
    .then(response => response.json())
    .then(result => {
        console.log(JSON.stringify(result))
        
        var server_code = JSON.stringify(result['code'])
        var server_response = JSON.stringify(result['response'])
        if (server_code == 200) {
            alert("SUKCES!\nPomyślnie zmieniono stan magazynowy!")
            location.replace("/warehouse");}
        else if(server_code == 401) {
            alert("BŁĄD!\nKomunikat serwera: " + server_response)}
        else if(server_code == 500) {
            alert("BŁĄD!\nKomunikat serwera: " + server_response)}
        else {
            alert("BŁĄD NIEOKREŚLONY!\nBrak uwzględnionego kodu.\nZakres uwzględnionych błędów (200, 401, 500)")}
    });
});

$('#editbtn3').click(function() {
    item_id = $('#item_id').val();

    data = {
        "item_id": item_id
    };

    fetch("/chemini-api/item-delete-row",{
    method: 'DELETE',
    headers: main_headers,
    body: JSON.stringify(data)})
    .then(response => response.json())
    .then(result => {
        console.log(JSON.stringify(result))
        
        var server_code = JSON.stringify(result['code'])
        var server_response = JSON.stringify(result['response'])
        if (server_code == 200) {
            alert("SUKCES!\nPomyślnie usunięto!")
            location.replace("/warehouse");}
        else if(server_code == 401) {
            alert("BŁĄD!\nKomunikat serwera: " + server_response)}
        else if(server_code == 500) {
            alert("BŁĄD!\nKomunikat serwera: " + server_response)}
        else {
            alert("BŁĄD NIEOKREŚLONY!\nBrak uwzględnionego kodu.\nZakres uwzględnionych błędów (200, 401, 500)")}
    });
});