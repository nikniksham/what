let productsOnPage = 20;

function openPage(page) {
    let products = document.getElementById('products');
    for (let i=0; i < products.children.length; i++) {
        if ((i > productsOnPage * (page - 1)) && (i < productsOnPage * page + 1)) {
            products.children[i].classList.remove('hidden');
        }
        else {
            products.children[i].classList.add('hidden');
        }
    }
    let pagination = document.getElementById('pagination');
    for (let i=0; i < pagination.children.length; i++) {
        if (pagination.children[i].id == page) {
            pagination.children[i].classList.add('active');
        } else {
            pagination.children[i].classList.remove('active');
        }
    }
    window.scrollTo(0, 0);
}

openPage(1)