const cupForm = document.querySelector("#cupcake-form")
cupList = document.querySelector("ul");

window.addEventListener('load', (event) => {
    displayCupcakes();
  });

async function getCupcakes() {
    const res = await axios.get("http://127.0.0.1:5000/api/cupcakes");
    return res.data.cupcakes;
}

async function displayCupcakes() {
    let liItems = "";
    const cupcakes = await getCupcakes();
    for (c of cupcakes){
        li = `<li><h3>${c.flavor}</h3><img src="${c.image}"><p>Size: ${c.size} Rating: ${c.rating}</p></li>`;
        liItems += ` ${li}`;
    }
    cupList.innerHTML = liItems;
}

function addCupcakeLi(cupData) {
    li = document.createElement("li");
    li.innerHTML = `<h3>${cupData.flavor}</h3><img src="${cupData.image}"><p>Size: ${cupData.size} Rating: ${cupData.rating}</p>`;
    cupList.append(li);
}

cupForm.addEventListener('submit', async function(e){
    e.preventDefault();
    cupcake = extractFormData()
    newCup =  await addCupcake(cupcake.flavor, cupcake.size, cupcake.rating, cupcake.image);
    addCupcakeLi(newCup.data.cupcake);
    cupList.reset();
})

async function addCupcake(flavor, size, rating, image){
    data = {"flavor": flavor, "size": size, "rating": rating, "image": image};
    const resp = await axios.post("http://127.0.0.1:5000/api/cupcakes", data);
    return resp;
}

function extractFormData(){
    const flavor = document.querySelector("#flavor").value;
    const size = document.querySelector("#size").value;
    const rating = document.querySelector("#rating").value;
    document.querySelector("#image-url").value;
    let image = document.querySelector("#image-url").value;
    image = image === "" ? null : image;
    return {"flavor": flavor, "size": size, "rating": rating, "image": image};
}


