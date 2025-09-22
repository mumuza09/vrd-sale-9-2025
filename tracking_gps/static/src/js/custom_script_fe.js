/** @odoo-module **/
import { session } from "@web/session";

console.log("Custom JS loaded on all pages! FE");

// Example: Add a custom class to the body tag
document.addEventListener('DOMContentLoaded', function () {
    // document.body.classList.add('custom-class');
});

// console.log(session);

// function getLocation() {
//     if (navigator.geolocation) {
//         navigator.geolocation.getCurrentPosition(
//             (position) => {
//                 const lat = position.coords.latitude;
//                 const lon = position.coords.longitude;
//                 console.log(`Latitude: ${lat}, Longitude: ${lon}`);

//                 // You can send this data to a server if needed
//                 fetch('/save-location', {
//                     method: 'POST',
//                     headers: { 'Content-Type': 'application/json' },
//                     body: JSON.stringify({ latitude: lat, longitude: lon })
//                 })
//                 .then(response => response.json())
//                 .then(data => console.log(data));

//                 // fetch('/web/dataset/call_kw', {
//                 //     method: 'POST',
//                 //     headers: { 'Content-Type': 'application/json' },
//                 //     body: JSON.stringify({
//                 //         jsonrpc: "2.0",
//                 //         method: "call",
//                 //         params: {
//                 //             model: "partner.location",
//                 //             method: "create",
//                 //             args: [{
//                 //                 partner_id: session.user_id,  
//                 //                 latitude: lat,
//                 //                 longitude: lon
//                 //             }],
//                 //             kwargs: {},
//                 //         }
//                 //     })
//                 // });

//             },
//             (error) => {
//                 console.error("Error getting location:", error.message);
//             }
//         );
//     } else {
//         console.error("Geolocation is not supported by this browser.");
//     }

//     // setInterval(getLocation, 300000);
// }

// // Run the function every 5 minutes (300000 ms)
// setInterval(getLocation, 300000);

// // Run immediately on page load
// getLocation();


