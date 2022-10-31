// Kartoteka nie została utworzona! Prawdopodobne problemy: referencja lub kod towaru istnieje już w bazie, któryś z wpisów nie jest poprawny (np. zastosowanie przy cenie ',' zamiast '.' lub wpisanie tekstu w miejscu gdzie powinny być cyfry (stan minimalny, zakup, cena, kod))
main_headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJEYW1pYW4ifQ.49JmaHCvE7bePDuEylskD344AAULyLAB9FPf8hRwHTM'
};



// item_name = $('#name').val();
// manufacturer = $('#manufacturer').val();
// reference = $('#reference').val();
// stack_min = $('#stack_min').val();
// buy = $('#buy').val();
// sell = $('#sell').val();
// description = $('#description').val();
// code = $('#code').val();
// used = document.getElementById("isused").checked;



// $('#button').click(function() {
  
//   item_name = $('#name').val();
//   manufacturer = $('#manufacturer').val();
//   reference = $('#reference').val();
//   stack_min = $('#stack_min').val();
//   buy = $('#buy').val();
//   sell = $('#sell').val();
//   description = $('#description').val();
//   code = $('#code').val();
//   used = document.getElementById("isused").checked;
    
//   var forms = document.querySelectorAll('.needs-validation')

//   _stack_min = parseFloat(stack_min);
//   _buy = parseFloat(buy);
//   _sell = parseFloat(sell);

//   // Loop over them and prevent submission
//   Array.prototype.slice.call(forms)
//     .forEach(function (form) {
//       form.addEventListener('submit', function (event) {
//         if (!form.checkValidity()) {
//           event.preventDefault()
//           event.stopPropagation()
//         }

//         form.classList.add('was-validated')
//       }, false)
      
//       if (form.checkValidity()) {
//           console.log(_stack_min, _buy, _sell)

//           data = {
//             "item_name": item_name,
//             "manufacturer": manufacturer,
//             "reference": reference,
//             "stack_min": stack_min,
//             "buy": buy,
//             "sell": sell,
//             "description": description,
//             "code": code,
//             "used": used
//           };
    
//           console.log(data)
      
//           fetch("/chemini-api/additem",{
//           method: 'PUT',
//           headers: main_headers,
//           body: JSON.stringify(data)})
//           .then(response => response.json())
//           .then(result => {
//               console.log(JSON.stringify(result))
              
//               var server_code = JSON.stringify(result['code'])
//               var server_response = JSON.stringify(result['response'])
//               if (server_code == 200) {
//                   alert("SUKCES!\nPomyślnie dodano kartotekę.")
//                   location.replace("/warehouse");}
//               else if(server_code == 401) {
//                   alert("BŁĄD!\nKomunikat serwera: " + server_response)}
//               else if(server_code == 500) {
//                   alert("BŁĄD bazy danych!\n\nKartoteka nie została utworzona!\nPrawdopodobne problemy:\n- referencja lub kod towaru istnieje już w bazie\n- któryś z wpisów nie jest poprawny (np. wpisanie tekstu w miejscu gdzie powinny być cyfry (stan minimalny, zakup, cena, kod)) ")}
//               else {
//                   alert("BŁĄD NIEOKREŚLONY!\nBrak uwzględnionego kodu.\nZakres uwzględnionych błędów (200, 401, 500)")}
//           });
//         }
//       }
//     )
// });




// $('#button').click(function() {
//   var forms = document.querySelectorAll('.needs-validation')

//   // Loop over them and prevent submission
//   Array.prototype.slice.call(forms)
//     .forEach(function (form) {
//       form.addEventListener('submit', function (event) {
//         if (!form.checkValidity()) {
//           event.preventDefault()
//           event.stopPropagation()
//         }

//         form.classList.add('was-validated')
//       }, false)
      
//       if (form.checkValidity()) {
//         send();
//       }
//     })
// })

// function send(){

//     data = {
//         "item_name": item_name,
//         "manufacturer": manufacturer,
//         "reference": reference,
//         "stack_min": stack_min,
//         "buy": buy,
//         "sell": sell,
//         "description": description,
//         "code": code,
//         "used": used
//     };

//     console.log(data)
//     // console.log(description)

//     fetch("/chemini-api/additem",{
//     method: 'PUT',
//     headers: main_headers,
//     body: JSON.stringify(data)})
//     .then(response => response.json())
//     .then(result => {
//         console.log(JSON.stringify(result))
        
//         var server_code = JSON.stringify(result['code'])
//         var server_response = JSON.stringify(result['response'])
//         if (server_code == 200) {
//             alert("SUKCES!\nPomyślnie dodano kartotekę.")
//             location.replace("/warehouse");}
//         else if(server_code == 401) {
//             alert("BŁĄD!\nKomunikat serwera: " + server_response)}
//         else if(server_code == 500) {
//             alert("BŁĄD bazy danych!\nKartoteka nie została utworzona! Prawdopodobne problemy: referencja lub kod towaru istnieje już w bazie, któryś z wpisów nie jest poprawny (np. zastosowanie przy cenie ',' zamiast '.' lub wpisanie tekstu w miejscu gdzie powinny być cyfry (stan minimalny, zakup, cena, kod)) ")}
//         else {
//             alert("BŁĄD NIEOKREŚLONY!\nBrak uwzględnionego kodu.\nZakres uwzględnionych błędów (200, 401, 500)")}
//     });
// }




$('#button').click(function() {
  
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

  fetch("/chemini-api/additem",{
  method: 'PUT',
  headers: main_headers,
  body: JSON.stringify(data)})
  .then(response => response.json())
  .then(result => {
      console.log(JSON.stringify(result))
      
      var server_code = JSON.stringify(result['code'])
      var server_response = JSON.stringify(result['response'])
      if (server_code == 200) {
          alert("SUKCES!\nPomyślnie dodano kartotekę.")
          location.replace("/warehouse");}
      else if(server_code == 401) {
          alert("BŁĄD!\nKomunikat serwera: " + server_response)}
      else if(server_code == 500) {
          alert("BŁĄD bazy danych!\n\nKartoteka nie została utworzona!\nPrawdopodobne problemy:\n- referencja lub kod towaru istnieje już w bazie\n- któryś z wpisów nie jest poprawny (np. wpisanie tekstu w miejscu gdzie powinny być cyfry (stan minimalny, zakup, cena, kod)) ")}
      else {
          alert("BŁĄD NIEOKREŚLONY!\nBrak uwzględnionego kodu.\nZakres uwzględnionych błędów (200, 401, 500)")}
  });
});
