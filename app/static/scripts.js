
document.addEventListener('DOMContentLoaded', function() {
  // Mobile menu toggle
  const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
  if (mobileMenuToggle) {
    mobileMenuToggle.addEventListener('click', function() {
      const sidebar = document.querySelector('.sidebar');
      sidebar.classList.toggle('active');
    });
  }
  
  // Ticket status badges color
  document.querySelectorAll('.badge-new').forEach(badge => {
    badge.style.backgroundColor = '#e74c3c';
  });
  
  document.querySelectorAll('.badge-in-progress').forEach(badge => {
    badge.style.backgroundColor = '#f39c12';
  });
  
  document.querySelectorAll('.badge-resolved').forEach(badge => {
    badge.style.backgroundColor = '#2ecc71';
  });
  
  document.querySelectorAll('.badge-closed').forEach(badge => {
    badge.style.backgroundColor = '#7f8c8d';
  });
  
  // Automatically close alerts after 5 seconds
  setTimeout(function() {
    document.querySelectorAll('.alert').forEach(alert => {
      alert.style.opacity = '0';
      setTimeout(() => {
        alert.style.display = 'none';
      }, 500);
    });
  }, 5000);
  
  // Handle confirmation modals
  document.querySelectorAll('[data-confirm]').forEach(button => {
    button.addEventListener('click', function(e) {
      if (!confirm(this.getAttribute('data-confirm'))) {
        e.preventDefault();
      }
    });
  });
  
  // Date picker initialization
  const datePickers = document.querySelectorAll('.datepicker');
  if (datePickers.length > 0) {
    datePickers.forEach(picker => {
      new Pikaday({
        field: picker,
        format: 'DD/MM/YYYY'
      });
    });
  }
  
  // Rich text editor initialization
  const richTextAreas = document.querySelectorAll('.rich-textarea');
  if (richTextAreas.length > 0) {
    richTextAreas.forEach(area => {
      ClassicEditor
        .create(area)
        .catch(error => {
          console.error(error);
        });
    });
  }
});

// Function to show/hide elements
function toggleElement(elementId) {
  const element = document.getElementById(elementId);
  if (element.style.display === 'none' || element.style.display === '') {
    element.style.display = 'block';
  } else {
    element.style.display = 'none';
  }
}

// Function to copy text to clipboard
function copyToClipboard(text) {
  const textArea = document.createElement('textarea');
  textArea.value = text;
  document.body.appendChild(textArea);
  textArea.select();
  document.execCommand('copy');
  document.body.removeChild(textArea);
  
  // Show a temporary notification
  const notification = document.createElement('div');
  notification.className = 'copy-notification';
  notification.textContent = 'Copié !';
  document.body.appendChild(notification);
  
  setTimeout(() => {
    notification.style.opacity = '0';
    setTimeout(() => {
      document.body.removeChild(notification);
    }, 500);
  }, 1500);
}
