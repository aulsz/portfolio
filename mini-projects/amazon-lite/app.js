const products = [
  { id: 1, name: 'Wireless Headphones', price: 49.99, img: 'https://picsum.photos/seed/a1/320/220' },
  { id: 2, name: 'Mechanical Keyboard', price: 79.99, img: 'https://picsum.photos/seed/a2/320/220' },
  { id: 3, name: 'USB-C Hub', price: 29.99, img: 'https://picsum.photos/seed/a3/320/220' },
  { id: 4, name: 'Desk Lamp', price: 24.99, img: 'https://picsum.photos/seed/a4/320/220' },
  { id: 5, name: 'Smart Watch', price: 119.99, img: 'https://picsum.photos/seed/a5/320/220' },
  { id: 6, name: 'Monitor Stand', price: 34.99, img: 'https://picsum.photos/seed/a6/320/220' }
];
const grid = document.getElementById('grid');
const cartBtn = document.getElementById('cartBtn');
const cartPanel = document.getElementById('cart');
const cartItems = document.getElementById('cartItems');
const cartCount = document.getElementById('cartCount');
const totalEl = document.getElementById('total');
const search = document.getElementById('search');
let cart = [];
function renderProducts(list){grid.innerHTML=list.map(p=>`<article class="card"><img src="${p.img}" alt="${p.name}" /><h3>${p.name}</h3><p class="price">$${p.price.toFixed(2)}</p><button data-id="${p.id}">Add to cart</button></article>`).join('')}
function renderCart(){cartCount.textContent=cart.length;const grouped=cart.reduce((a,p)=>(a[p.id]=(a[p.id]||{...p,qty:0}),a[p.id].qty++,a),{});const items=Object.values(grouped);cartItems.innerHTML=items.length?items.map(i=>`<p>${i.name} x${i.qty} — $${(i.qty*i.price).toFixed(2)}</p>`).join(''):'<p>Cart is empty.</p>';totalEl.textContent=cart.reduce((s,p)=>s+p.price,0).toFixed(2)}
grid.addEventListener('click',(e)=>{if(e.target.tagName!=='BUTTON')return;const id=Number(e.target.dataset.id);const p=products.find(x=>x.id===id);if(p)cart.push(p);renderCart();});
cartBtn.addEventListener('click',()=>cartPanel.classList.toggle('hidden'));
search.addEventListener('input',()=>{const q=search.value.toLowerCase();renderProducts(products.filter(p=>p.name.toLowerCase().includes(q)));});
renderProducts(products);renderCart();
