let productsOnPage = 20;

function openPage(page) {
    let products = document.getElementById('products');
    console.log(products.children[0]);
    console.log(products.children.length);
    for (let i=0; i < products.children.length; i++) {
        if ((i > productsOnPage * (page - 1)) && (i < productsOnPage * page + 1)) {
            console.log(i);
            products.children[i].classList.remove('hidden');
        }
        else {
            products.children[i].classList.add('hidden');
        }
    }
}

openPage(1)