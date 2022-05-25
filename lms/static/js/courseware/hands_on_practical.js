// regex to allow only letters and spaces in input field
jQuery.validator.addMethod("lettersonly", function(value, element) {
    return this.optional(element) || /^[a-zA-Z\s]*$/i.test(value);
  })
  
  // It checks all the input field of Form And Displays the error if any
  $("#registration-form").validate({
      rules: {
          FullName: {
              minlength: 3,
              maxlength: 50,
              required: true,
              lettersonly: true
          },
          Email: {
              required: true,
              email: true
          },
          PhoneNumber: {
              required: true,
              number: true,
              minlength: 10,
              maxlength: 10
          },
          ContactName: {
              minlength: 3,
              maxlength: 50,
              required: true,
              lettersonly: true
          },
          ContactPhoneNumber: {
              required: true,
              number: true,
              minlength: 10,
              maxlength: 10
          },
          practical_name:{
              required: true
          }
  
      }
  });
  
  
  // Generates the csrftoken for post data
  function getCookie(name) {
      var cookieValue = null;
      if (document.cookie && document.cookie !== '') {
          var cookies = document.cookie.split(';');
          for (var i = 0; i < cookies.length; i++) {
              var cookie = cookies[i].trim();
              // Does this cookie string begin with the name we want?
              if (cookie.substring(0, name.length + 1) === (name + '=')) {
                  cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                  break;
              }
          }
      }
      return cookieValue;
  }
  
  var csrftoken = getCookie('csrftoken')
  
  $(".book-now").on("click", function (e) {
      // to check if form is valid or not
      if ($('#registration-form').valid()) {
  
          var form_data = $('#registration-form').serializeArray().reduce(function (obj, item) {
              obj[item.name] = item.value;
              return obj;
          }, {});
  
          $.ajax({
              // ajax call to check if user is already registered
              url: "/hands-on-practical/api/student-pratical-data/",
              type: "GET",
              data: {
                  email: form_data['Email'],
                  practical_name: form_data['practical_name']
              },
              success: function (data) {
                  console.log(data)
                  if (data['user_exist_data']) {
                      // If User has already registered
                      $(".already-registered").css("display", "block")
                      $(".student-registered").css("display", "none")
                      $(".seat-fulled").css("display", "none")
                  }
                  else if (data['seats_fulled']){
                      // if seats are full in practical
                      $(".seat-fulled").css("display", "block")
                      $(".student-registered").css("display", "none")
                      $(".already-registered").css("display", "none")
                  }
                  else {
                      // if user has not registered
                      
                      $(".already-registered").css("display", "none")
                      $(".seat-fulled").css("display", "none")
                      $.ajax({
                          // ajax call to save the user details for sesion
                          url: "/hands-on-practical/api/student-pratical-data/",
                          type: "POST",
                          headers: {
                              'X-CSRFToken': csrftoken
                          },
                          data: {
                              course_id: form_data['course_id'],
                              full_name: form_data['FullName'],
                              email: form_data['Email'],
                              phone_number: form_data['PhoneNumber'],
                              contact_name: form_data['ContactName'],
                              contact_phone_number: form_data['ContactPhoneNumber'],
                              other_requirements: form_data['OtherRequirements'],
                              other_comments: form_data['Comments'],
                              practical_name: form_data['practical_name']
                          },
                          success: function (data) {
                              // POST request return
                              $(".student-registered").css("display", "block")
                              $("#registration-form").css("display", "none")
  
                          },
                          error: function (data) {
                              // to display errors if there are any
                              $.each(data['responseJSON'], function (key, value) {
                                  $("." + key).text(value);
                              });
                          }
                      });
                  }
  
  
              }
  
          })
  
          $('#registration-form').trigger("reset");
      }
  
  })
  
  // $(".upcoming-events").on('click', function (e) {
  //     $("#registration-form").css("display", "none")
  //     $("#calendar").css("display", "block", "important")
  //     $("#calendar").css("height", "1400px", "important")
  // })
  
  
  // $(".form-view").on('click', function (e) {
  //     $(".tab-content").css("display", "none")
  //     $("#registration-form").css("display", "block")
  // })
  