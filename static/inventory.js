$("#resetList").click(function() {
    if (window.confirm("Czy na pewno chcesz zresetować listę?")){
        
        fetch("/inventory/reset",{
        method: "POST"})
        .then(response => response.json())
        .then(result => {
            console.log(JSON.stringify(result))
            
            var server_response = result['response']
            var server_msg = result['msg']
            
            if (server_response == "success") {
                alert(server_msg)
                location.replace("/inventory");
              }
            else if(server_response == "error") {
                alert(server_msg)
            //   resp = server_msg.replace(/\n/g, "<br />")
            //   document.getElementById('error').innerHTML = resp;
            }
            else {
                alert("BŁĄD NIEOKREŚLONY!\nBrak uwzględnionego kodu.\nZakres uwzględnionych błędów (200, 401, 500)")}
        });
    }
})

$("#acceptInventory").click(function() {
    if (window.confirm("Zatwierdzenie spowoduje zmiany w istniejącej bazie danych!\nCzy na pewno chcesz zresetować inwentaryzację?")){
        
        fetch("/inventory/accept",{
        method: "POST"})
        .then(response => response.json())
        .then(result => {
            console.log(JSON.stringify(result))
            
            var server_response = result['response']
            var server_msg = result['msg']
            
            if (server_response == "success") {
                alert(server_msg)
                location.replace("/warehouse");
              }
            else if(server_response == "error") {
                alert(server_msg)
            //   resp = server_msg.replace(/\n/g, "<br />")
            //   document.getElementById('error').innerHTML = resp;
            }
            else {
                alert("BŁĄD NIEOKREŚLONY!\nBrak uwzględnionego kodu.\nZakres uwzględnionych błędów (200, 401, 500)")}
        });
    }
})