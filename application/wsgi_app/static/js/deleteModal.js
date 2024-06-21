const deleteModalEl = document.getElementById('deleteModal');
deleteModalEl.addEventListener('show.bs.modal', function (event) {
    let url = event.relatedTarget.dataset.url;
    let form = this.querySelector('form');
    form.action = url;
    let span = this.querySelector('.delete-title');
    span.textContent = event.relatedTarget.dataset.name;
});

deleteModalEl.querySelector('form').addEventListener('submit', function (event) {
    let deleteCover = this.parentElement.querySelector('#delete-cover').checked ? '1' : '0';
    let postUrl = new URL(this.action);
    postUrl.searchParams.set('delete_cover', deleteCover);
    this.action = postUrl;
})