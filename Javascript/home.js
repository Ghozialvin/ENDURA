const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('scroll-show');
      entry.target.classList.remove('scroll-hidden');
    } else {
      entry.target.classList.remove('scroll-show');
      entry.target.classList.add('scroll-hidden');
    }
  });
});
document.querySelectorAll('.onepages, .program, .features, .about, .person-card, .program-img, .content').forEach((section) => {
  section.classList.add('scroll-hidden');
  observer.observe(section);
});
