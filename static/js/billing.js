
document.addEventListener("DOMContentLoaded", function () {

    // =====================================
    // ELEMENTS
    // =====================================

    const productList = document.getElementById("billingProductList");
    const searchInput = document.getElementById("productSearch");
    const categoryFilter = document.getElementById("categoryFilter");

    const cartItems = document.getElementById("cartItems");
    const cartCount = document.getElementById("cartItemCount");

    const placeOfSupply = document.getElementById("placeOfSupply");
    const paidAmountInput = document.getElementById("paidAmount");

    const generateBillBtn = document.getElementById("generateBillBtn");

    if (!productList || !searchInput) return;

    const apiUrl = productList.dataset.apiUrl;
    const SHOP_STATE_CODE = "27";

    let cart = [];
    let products = [];

    let currentPage = 1;
    let totalPages = 1;
    let currentSearch = "";
    let currentCategory = "";

    let currentGrandTotal = 0;

    // =====================================
    // HELPER FUNCTIONS
    // =====================================

    function money(value) {
        return "₹" + Number(value).toFixed(2);
    }

    function roundMoney(value) {
        return Math.round(
            (value + Number.EPSILON) * 100
        ) / 100;
    }

    function getCSRFToken() {
        return document.querySelector(
            "#csrfForm [name=csrfmiddlewaretoken]"
        )?.value;
    }

    // =====================================
    // LOAD PRODUCTS
    // =====================================

    async function loadProducts(query = currentSearch, page = 1) {

        currentSearch = query;
        currentPage = page;

        productList.innerHTML = `
            <div class="billing-empty-state">
                <p>Loading products...</p>
            </div>
        `;

        try {

            const url = new URL(apiUrl, window.location.origin);

            url.searchParams.set("page", currentPage);

            if (currentSearch.trim()) {
                url.searchParams.set("q", currentSearch.trim());
            }

            if (currentCategory) {
                url.searchParams.set("category", currentCategory);
            }

            const response = await fetch(url);

            if (!response.ok) {
                throw new Error("Unable to fetch products.");
            }

            const data = await response.json();

            if (!data.success) {
                throw new Error("Product API failed.");
            }

            products = data.products;
            totalPages = data.total_pages || 1;

            renderProducts();
            updatePagination();

        } catch (error) {

            console.error(error);

            productList.innerHTML = `
                <div class="billing-empty-state">
                    <p>Unable to load products.</p>
                    <p>Please refresh the page.</p>
                </div>
            `;
        }
    }

    // =====================================
    // RENDER PRODUCTS
    // =====================================

    function renderProducts() {

        productList.innerHTML = "";

        if (products.length === 0) {

            productList.innerHTML = `
                <div class="billing-empty-state">
                    <p>No products found.</p>
                </div>
            `;

            return;
        }

        products.forEach(product => {

            const stock = Number(product.stock_quantity);
            const price = Number(product.selling_price);

            const card = document.createElement("div");
            card.className = "billing-product-card";

            const name = document.createElement("h3");
            name.textContent = product.name;

            const category = document.createElement("p");
            category.textContent = "Category: " + product.category;

            const stockInfo = document.createElement("p");
            stockInfo.textContent =
                `Stock: ${stock} ${product.unit}`;

            const priceInfo = document.createElement("div");
            priceInfo.className = "billing-product-price";
            priceInfo.textContent = money(price);

            const gstInfo = document.createElement("p");
            gstInfo.textContent =
                `GST: ${product.gst_rate}% (Extra)`;

            const button = document.createElement("button");
            button.className = "add-to-cart-btn";
            button.type = "button";

            if (stock <= 0) {

                button.textContent = "Out of Stock";
                button.disabled = true;

            } else {

                button.textContent = "Add to Cart";

                button.addEventListener("click", function () {
                    addToCart(product);
                });
            }

            card.append(
                name,
                category,
                stockInfo,
                priceInfo,
                gstInfo,
                button
            );

            productList.appendChild(card);
        });
    }

    // =====================================
    // PAGINATION
    // =====================================

    function updatePagination() {

        const prevButton = document.getElementById("prevPage");
        const nextButton = document.getElementById("nextPage");
        const pageInfo = document.getElementById("pageInfo");

        pageInfo.textContent =
            `Page ${currentPage} of ${totalPages}`;

        prevButton.disabled = currentPage <= 1;
        nextButton.disabled = currentPage >= totalPages;
    }

    // =====================================
    // ADD TO CART
    // =====================================

    function addToCart(product) {

        const existing = cart.find(
            item => item.id === product.id
        );

        const stock = Number(product.stock_quantity);

        if (existing) {

            if (existing.quantity + 1 > stock) {
                alert("Available stock limit reached!");
                return;
            }

            existing.quantity += 1;

        } else {

            if (stock < 1) {
                alert("Product is out of stock!");
                return;
            }

            cart.push({
                id: product.id,
                name: product.name,
                price: Number(product.selling_price),
                gst: Number(product.gst_rate),
                stock: stock,
                unit: product.unit,
                quantity: 1
            });
        }

        renderCart();
    }

    // =====================================
    // UPDATE QUANTITY
    // =====================================

    function updateQuantity(productId, change) {

        const item = cart.find(
            product => product.id === productId
        );

        if (!item) return;

        const newQuantity = item.quantity + change;

        if (newQuantity <= 0) {

            cart = cart.filter(
                product => product.id !== productId
            );

        } else if (newQuantity > item.stock) {

            alert("Available stock limit reached!");
            return;

        } else {

            item.quantity = newQuantity;
        }

        renderCart();
    }

    // =====================================
    // REMOVE PRODUCT
    // =====================================

    function removeProduct(productId) {

        cart = cart.filter(
            product => product.id !== productId
        );

        renderCart();
    }

    // =====================================
    // RENDER CART
    // =====================================

    function renderCart() {

        cartItems.innerHTML = "";

        if (cart.length === 0) {

            cartItems.innerHTML = `
                <tr>
                    <td colspan="5" class="empty-cart">
                        No products added yet
                    </td>
                </tr>
            `;
        }

        cart.forEach(item => {

            const row = document.createElement("tr");

            const productCell = document.createElement("td");
            productCell.textContent = item.name;

            const qtyCell = document.createElement("td");

            const minus = document.createElement("button");
            minus.textContent = "−";
            minus.type = "button";

            minus.addEventListener("click", () => {
                updateQuantity(item.id, -1);
            });

            const qtyText = document.createElement("span");
            qtyText.textContent = ` ${item.quantity} `;

            const plus = document.createElement("button");
            plus.textContent = "+";
            plus.type = "button";

            plus.addEventListener("click", () => {
                updateQuantity(item.id, 1);
            });

            qtyCell.append(minus, qtyText, plus);

            const priceCell = document.createElement("td");
            priceCell.textContent = money(item.price);

            const totalCell = document.createElement("td");
            totalCell.textContent =
                money(item.price * item.quantity);

            const removeCell = document.createElement("td");

            const removeButton = document.createElement("button");
            removeButton.textContent = "✕";
            removeButton.type = "button";
            removeButton.style.color = "red";

            removeButton.addEventListener("click", () => {
                removeProduct(item.id);
            });

            removeCell.appendChild(removeButton);

            row.append(
                productCell,
                qtyCell,
                priceCell,
                totalCell,
                removeCell
            );

            cartItems.appendChild(row);
        });

        calculateTotals();

        const totalQuantity = cart.reduce(
            (sum, item) => sum + item.quantity,
            0
        );

        cartCount.textContent = `${totalQuantity} Items`;
    }

    // =====================================
    // GST CALCULATION
    // =====================================

    function calculateTotals() {

        let subtotal = 0;
        let cgst = 0;
        let sgst = 0;
        let igst = 0;

        const customerState = placeOfSupply.value.trim();

        cart.forEach(item => {

            const taxable = roundMoney(
                item.price * item.quantity
            );

            const tax = roundMoney(
                taxable * item.gst / 100
            );

            subtotal += taxable;

            if (customerState === SHOP_STATE_CODE) {

                const halfTax = roundMoney(tax / 2);

                cgst += halfTax;
                sgst += tax - halfTax;

            } else if (/^\d{2}$/.test(customerState)) {

                igst += tax;
            }
        });

        subtotal = roundMoney(subtotal);
        cgst = roundMoney(cgst);
        sgst = roundMoney(sgst);
        igst = roundMoney(igst);

        currentGrandTotal = roundMoney(
            subtotal + cgst + sgst + igst
        );

        document.getElementById("billSubtotal").textContent =
            money(subtotal);

        document.getElementById("billCGST").textContent =
            money(cgst);

        document.getElementById("billSGST").textContent =
            money(sgst);

        document.getElementById("billIGST").textContent =
            money(igst);

        document.getElementById("billGrandTotal").textContent =
            money(currentGrandTotal);
    }

    // =====================================
    // PAYMENT BUTTONS
    // =====================================

    const fullPaymentBtn =
        document.getElementById("fullPaymentBtn");

    const partialPaymentBtn =
        document.getElementById("partialPaymentBtn");

    const fullUdharBtn =
        document.getElementById("fullUdharBtn");

    // FULL PAYMENT

    if (fullPaymentBtn) {

        fullPaymentBtn.addEventListener("click", function () {

            if (cart.length === 0) {
                alert("Please add products first.");
                return;
            }

            paidAmountInput.value =
                currentGrandTotal.toFixed(2);

        });
    }

    // PARTIAL PAYMENT

    if (partialPaymentBtn) {

        partialPaymentBtn.addEventListener("click", function () {

            if (cart.length === 0) {
                alert("Please add products first.");
                return;
            }

            paidAmountInput.value = "";
            paidAmountInput.placeholder =
                "Enter partial amount";

            paidAmountInput.focus();

        });
    }

    // FULL UDHAR

    if (fullUdharBtn) {

        fullUdharBtn.addEventListener("click", function () {

            if (cart.length === 0) {
                alert("Please add products first.");
                return;
            }

            paidAmountInput.value = "0";

        });
    }

    // =====================================
    // SEARCH
    // =====================================

    let searchTimer;

    searchInput.addEventListener("input", function () {

        clearTimeout(searchTimer);

        searchTimer = setTimeout(function () {
            loadProducts(searchInput.value, 1);
        }, 300);

    });

    // =====================================
    // CATEGORY FILTER
    // =====================================

    if (categoryFilter) {

        categoryFilter.addEventListener("change", function () {

            currentCategory = this.value;

            loadProducts(currentSearch, 1);

        });
    }

    // =====================================
    // PAGINATION BUTTONS
    // =====================================

    document.getElementById("prevPage").addEventListener(
        "click",
        function () {

            if (currentPage > 1) {
                loadProducts(currentSearch, currentPage - 1);
            }

        }
    );

    document.getElementById("nextPage").addEventListener(
        "click",
        function () {

            if (currentPage < totalPages) {
                loadProducts(currentSearch, currentPage + 1);
            }

        }
    );

    // =====================================
    // STATE CHANGE
    // =====================================

    placeOfSupply.addEventListener("input", calculateTotals);

    // =====================================
    // GENERATE BILL
    // =====================================

    if (generateBillBtn) {

        generateBillBtn.addEventListener("click", async function () {

            if (cart.length === 0) {
                alert("Please add products to cart first.");
                return;
            }

            const csrfToken = getCSRFToken();

            if (!csrfToken) {
                alert("Security token missing. Please refresh the page.");
                return;
            }

            const customerName =
                document.getElementById("customerName").value.trim();

            const customerPhone =
                document.getElementById("customerPhone").value.trim();

            const paidValue = paidAmountInput.value.trim();

            // Blank means full payment.
            const paidAmount = paidValue === ""
                ? currentGrandTotal
                : Number(paidValue);

            if (
                !Number.isFinite(paidAmount) ||
                paidAmount < 0
            ) {
                alert("Please enter a valid paid amount.");
                return;
            }

            if (paidAmount > currentGrandTotal) {
                alert("Paid amount cannot exceed bill total.");
                return;
            }

            const dueAmount = roundMoney(
                currentGrandTotal - paidAmount
            );

            if (dueAmount > 0 && (!customerName || !customerPhone)) {
                alert(
                    "Customer name and mobile number are required for Udhar."
                );
                return;
            }

            const payload = {

                customer_name: customerName,

                customer_phone: customerPhone,

                customer_gstin:
                    document.getElementById("customerGstin").value.trim(),

                place_of_supply: placeOfSupply.value.trim(),

                payment_method:
                    document.getElementById("paymentMethod").value,

                paid_amount: paidAmount.toFixed(2),

                items: cart.map(item => ({
                    product_id: item.id,
                    quantity: item.quantity
                }))
            };

            const billApiUrl = generateBillBtn.dataset.apiUrl;

            generateBillBtn.disabled = true;
            generateBillBtn.textContent = "Processing...";

            try {

                const response = await fetch(billApiUrl, {

                    method: "POST",

                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken
                    },

                    body: JSON.stringify(payload)

                });

                const data = await response.json();

                if (!response.ok || !data.success) {
                    throw new Error(
                        data.message || "Bill generation failed."
                    );
                }

                alert(
                    "Bill Generated Successfully!\n\n" +
                    "Invoice: " + data.invoice_number + "\n" +
                    "Grand Total: " + money(data.grand_total) + "\n" +
                    "Paid: " + money(data.paid_amount) + "\n" +
                    "Due: " + money(data.due_amount) + "\n" +
                    "Status: " + data.payment_status
                );

                // CLEAR CART

                cart = [];

                renderCart();

                paidAmountInput.value = "";

                document.getElementById("customerName").value = "";
                document.getElementById("customerPhone").value = "";
                document.getElementById("customerGstin").value = "";

                loadProducts(currentSearch, currentPage);

            } catch (error) {

                alert(error.message);

                console.error("Billing error:", error);

            } finally {

                generateBillBtn.disabled = false;
                generateBillBtn.textContent = "Generate Bill";

            }

        });
    }

    // =====================================
    // INITIAL LOAD
    // =====================================

    loadProducts();
    renderCart();

    
    // =====================================
    // CUSTOMER AUTOCOMPLETE
    // =====================================

    const customerNameInput =
        document.getElementById("customerName");

    const customerPhoneInput =
        document.getElementById("customerPhone");

    const customerGstinInput =
        document.getElementById("customerGstin");

    const customerSuggestions =
        document.getElementById("customerSuggestions");

    let customerSearchTimer;
    let customerSearchRequestId = 0;

    function hideCustomerSuggestions() {
        customerSuggestions.innerHTML = "";
        customerSuggestions.style.display = "none";
    }

    function renderCustomerSuggestions(customers) {

        customerSuggestions.innerHTML = "";
        customerSuggestions.style.display = "block";

        if (customers.length === 0) {

            const emptyMessage = document.createElement("div");

            emptyMessage.className = "customer-no-results";

            emptyMessage.textContent =
                "No existing customer found. New customer will be saved after bill generation.";

            customerSuggestions.appendChild(emptyMessage);

            return;
        }

        customers.forEach(customer => {

            const button = document.createElement("button");

            button.type = "button";
            button.className = "customer-suggestion-item";

            const name = document.createElement("strong");
            name.textContent = customer.name;

            const details = document.createElement("span");

            details.textContent =
                customer.phone +
                (customer.gstin ? " | GSTIN: " + customer.gstin : "");

            button.append(name, details);

            button.addEventListener("click", function () {

                // Auto-fill customer details
                customerNameInput.value = customer.name;
                customerPhoneInput.value = customer.phone;
                customerGstinInput.value = customer.gstin || "";

                hideCustomerSuggestions();

            });

            customerSuggestions.appendChild(button);

        });
    }

    customerNameInput.addEventListener("input", function () {

        clearTimeout(customerSearchTimer);

        const query = this.value.trim();

        // User is typing a new or different customer.
        customerPhoneInput.value = "";
        customerGstinInput.value = "";

        if (query.length < 2) {
            hideCustomerSuggestions();
            return;
        }

        customerSearchTimer = setTimeout(async function () {

            const requestId = ++customerSearchRequestId;

            try {

                const url = new URL(
                    customerSuggestions.dataset.apiUrl,
                    window.location.origin
                );

                url.searchParams.set("q", query);

                const response = await fetch(url);

                if (!response.ok) {
                    throw new Error("Customer search failed.");
                }

                const data = await response.json();

                // Ignore an older response if a newer search was made.
                if (requestId !== customerSearchRequestId) {
                    return;
                }

                renderCustomerSuggestions(data.customers || []);

            } catch (error) {

                console.error("Customer search error:", error);

                hideCustomerSuggestions();

            }

        }, 300);

    });

    // Hide suggestions when clicking outside.
    document.addEventListener("click", function (event) {

        if (
            !event.target.closest(".customer-autocomplete")
        ) {
            hideCustomerSuggestions();
        }

    });

    // Hide suggestions on Escape key.
    customerNameInput.addEventListener("keydown", function (event) {

        if (event.key === "Escape") {
            hideCustomerSuggestions();
        }

    });


});
