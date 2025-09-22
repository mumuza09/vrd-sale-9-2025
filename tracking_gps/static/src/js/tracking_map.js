/** @odoo-module **/
import { useService } from "@web/core/utils/hooks";
import { Component, onMounted, useState, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

export class TrackingMap extends Component {
    setup() {
        this.orm = useService("orm");
        this.rpc = rpc;
        // this.mapRef = useRef("map");
        this.state = useState({
            users: [{name:'All', id: 0, employee_name: 'All'}],
            selectedUser: null,
            selectedDate: new Date().toISOString().split('T')[0],
            selectedTime: null,
            tracking: [],
            map: "/osm-map"
        });

        this.initMap();

        // this.location = [
        //     { "latitude": 13.7500, "longitude": 100.4913 },  // พระบรมมหาราชวัง (Grand Palace), กรุงเทพมหานคร
        //     { "latitude": 13.7520, "longitude": 100.4930 },  // วัดพระแก้ว (Wat Phra Kaew), กรุงเทพมหานคร
        //     { "latitude": 7.8804, "longitude": 98.2967 },    // หาดป่าตอง (Patong Beach), ภูเก็ต
        //     { "latitude": 13.7437, "longitude": 100.4880 },  // วัดอรุณราชวราราม (Wat Arun), กรุงเทพมหานคร
        //     { "latitude": 9.5125, "longitude": 100.0137 },   // เกาะสมุย (Koh Samui), สุราษฎร์ธานี
        //     { "latitude": 13.4878, "longitude": 99.9692 },   // ตลาดน้ำดำเนินสะดวก (Damnoen Saduak Floating Market), ราชบุรี
        //     { "latitude": 14.2810, "longitude": 98.6016 }    // อุทยานแห่งชาติทองผาภูมิ (Thong Pha Phum National Park), กาญจนบุรี
        // ]
        onMounted(this.loadUsers.bind(this));
       ;
        
    }
    async getUserId() {
        const sessionInfo = await this.rpc("/web/session/get_session_info");
        console.log("Session Info:", sessionInfo);
        this.state.selectedUser = sessionInfo.uid;
        this.state.currentCompanyId = sessionInfo.user_companies.current_company
        
    }
    async empName(users){
        const allEmployeeIds = users.flatMap(u => u.employee_ids);

        const employees = await this.orm.read("hr.employee", allEmployeeIds, ["id", "name"]);

        const employeeMap = Object.fromEntries(employees.map(e => [e.id, e.name]));

        users = users.map(u => {
            const employeeName = u.employee_ids.length ? employeeMap[u.employee_ids[0]] : null;
            return {
                ...u,
                employee_name: employeeName || u.name,
            };
        });     
        return users;
    }
    
    async loadUsers() {
        await this.getUserId()
        let user = await this.orm.searchRead("res.users", 
            [["employee_ids", "!=", false],["company_ids", "in", [this.state.currentCompanyId]]],
            ["id", "name", "partner_id","hr_icon_display","employee_ids"]
        );
        user = await this.empName(user);
        this.state.users = this.state.users.concat(user);
        console.log('Users:', this.state.users);
        await this.getLocationList()
        await this.loadLocations();
    }

    selectUser = async () => {
        console.log('selectUser', this.state.selectedUser)
        this.state.selectedTime = null;
        this.state.tracking = [];
        await this.getLocationList()
        await this.loadLocations();
    }
    selectDate = async () => {
        console.log('Selected Date:', this.state.selectedDate);
        this.state.selectedTime = null;
        this.state.tracking = [];
        await this.getLocationList();
        await this.loadLocations();
    }
    // selectTime = async () => {
    //     console.log('Selected Time:', this.state.selectedTime);
    //     await this.loadLocations();
    // }

    async getLocationList () {
        console.log('loadLocations')
        console.log("Fetching user with ID:", this.state.selectedUser);
        // if (!this.state.selectedUser) {
        //     console.error("selectedUser is null or undefined");
        //     return;
        // }
        let users
        if (this.state.selectedUser !== 0) {
            users = await this.orm.searchRead("res.users", [["id", "=" , this.state.selectedUser],["company_ids", "in", [this.state.currentCompanyId]]], ["id","name","partner_id","employee_ids"]);
            users = await this.empName(users);
            console.log('Users:', users);
            this.state.pinUser = users[0].name;    
        }

        const selectedDate = new Date(this.state.selectedDate);
        const startDate = new Date(selectedDate);
        startDate.setHours(startDate.getHours() - 7); // ถอยหลัง 1 วัน และปรับเป็น UTC
        startDate.setMinutes(0, 0, 0);
    
        const endDate = new Date(selectedDate);
        endDate.setHours(endDate.getHours() + 17); // ปรับเป็น UTC
        endDate.setMinutes(0, 0, 0);
    
        let filter = [["create_date", ">=", startDate.toISOString()], ["create_date", "<", endDate.toISOString()]]
        if (this.state.selectedUser !== 0) {
            filter.push(["partner_id", "=", users[0].partner_id[0]])
        }
        this.state.tracking = await this.orm.searchRead("partner.location", filter,
            ["id","partner_id", "longitude", "latitude", "create_date"] 
        );

        console.log('tracking:', this.state.tracking);

        // create_date

        // if (!this.state.tracking || this.state.tracking.length === 0) {
        //     console.warn("No tracking data available");
        //     return;
        // }
        // this.state.tracking.forEach(item => {
        //     const timePart = item.create_date.split(" ")[1];
        //     const timeHHMM = timePart.split(":").slice(0, 2).join(":");
        //     item.time = timeHHMM;
        // });
        let count = 0
        this.state.tracking.forEach(item => {
            const dateObj = new Date(item.create_date);
            dateObj.setHours(dateObj.getHours() + 7); // บวก 7 ชั่วโมง
            const hours = dateObj.getHours().toString().padStart(2, "0");
            const minutes = dateObj.getMinutes().toString().padStart(2, "0");
        
            const timeHHMM = `${hours}:${minutes}`;
            // console.log("Corrected timeHHMM:", timeHHMM);
            count += 1
            item.time = timeHHMM;
        });

        if (this.state.tracking.length > 0) {
            if (this.state.selectedUser !== 0) {
                this.setSliderConfig(0, this.state.tracking.length-1, 1);
                this.setSliderValue(this.state.tracking.length-1)    
            } else{

                function getLatestRecordsByPartner(data) {
                    return Object.values(
                        data.reduce((acc, obj) => {
                            const partnerId = obj.partner_id[0];
                
                            // ถ้า partner_id นี้ยังไม่มีใน acc หรือ obj ปัจจุบันมี create_date ใหม่กว่า
                            if (!acc[partnerId] || new Date(obj.create_date) > new Date(acc[partnerId].create_date)) {
                                acc[partnerId] = obj;
                            }
                
                            return acc;
                        }, {})
                    );
                }

                this.state.tracking = getLatestRecordsByPartner(this.state.tracking);

                this.setSliderConfig(0, 0, 1);
                this.setSliderValue(0)    
            }
        }
    }
    async loadLocations() {
        if (this.state.selectedUser !== null && this.state.selectedDate !== null ) {   
            // && this.state.tracking.length > 0
            let selectedName = this.state.selectedUser;
            let selectedDate = this.state.selectedDate;
            let selectedHour = parseInt(document.getElementById('timeSlider').value);
            let allLocations = this.state.tracking;
            console.log('selectedUser:', selectedName);
            console.log('selectedDate:', selectedDate);
            console.log('selectedHour:', selectedHour);
            console.log('allLocations:', allLocations);

            if(allLocations.length > 0){
                if (selectedName === 0) {
                    this.plotMarkers(allLocations);
                } else {
                    this.plotMarkers([allLocations[selectedHour]]);
                    this.state.selectedTime = allLocations[selectedHour].time;
                    console.log('selectedTime:', this.state.selectedTime);
                    await this.setUpTimeBar(this.state.selectedTime);
                }
            }else{
                this.state.tracking = [
                    {create_date:"2025-02-27 02:05:13",
                    latitude:13.775071545792505,
                    longitude:100.61024403990098,
                    time:"00:00"}
                ]
                this.plotMarkers(this.state.tracking);
                selectedHour = "00:00"
                this.state.selectedTime = "00:00"
                await this.setUpTimeBar("00:00");
            }

        }
    }

    initMap() {
        setTimeout(() => {
            const mapContainer = document.getElementById("map");
            if (!mapContainer) {
                console.error("Map container not found!");
                return;
            }

            this.map = L.map("map").setView([13.775071545792505, 100.61024403990098], 12); // first init https://maps.app.goo.gl/zWd75uV8TMWAf8Yh9
            L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
                attribution: "OpenStreetMap contributors",
            }).addTo(this.map);

            this.markers = [];

        }, 500);
    }

    plotMarkers(locations) {
        console.log("plotMarkers: ",locations);

        if (!Array.isArray(locations)) {
            console.error("Invalid locations data:", locations);
            return;
        }

        // check map ready or not
        if(this.map && L){
            // Remove old markers
            if(this.markers)
                this.markers.forEach(marker => this.map.removeLayer(marker));
            this.markers = [];

            const bounds = L.latLngBounds();

            locations.forEach(location => {
                console.log("location: ",location);
                console.log("location.latitude: ",location.latitude);
                console.log("location.longitude: ",location.longitude);
                console.log("this.state.pinUser: ",this.state.pinUser);
                let name = location.partner_id ? location.partner_id[1] : this.state.pinUser
                var url = "https://maps.google.com/?q="+ location.latitude + "," + location.longitude
                var popupLink='<a onclick="window.open(\'' + url + '\')">'+ name + " - " + location.time +'</a>';

                var marker = L.marker([location.latitude, location.longitude])
                    .addTo(this.map)
                    .bindPopup(popupLink);
                // all ต้อง push ล่าสุดของทุกคน
                this.markers.push(marker);
                bounds.extend([location.latitude, location.longitude]); // ขยาย bounds ให้ครอบคลุมทุกจุด

            });

            if (locations.length > 0) {
                // all อาจจะต้อง focus กทม หรือ หาจุดที่ห่างที่สุด แล้วปรับ zoom วางตรงกลาง
                if (locations.length === 1) {
                    this.map.setView([locations[0].latitude, locations[0].longitude], 12);
                } else {
                    this.map.fitBounds(bounds);
                }
            }

        }else{
            setTimeout(() => { this.plotMarkers(locations)  },200);
        }
        
    }

    async setUpTimeBar(selectedTime) {       
        const time_list = this.state.tracking.map(item => item.time);
        console.log('time_list:', time_list);
        console.log('selectedTime:', selectedTime);
    


        // กำหนดค่า min, max, step ของ slider
        this.setSliderConfig(0, time_list.length - 1, 1);
    
        const onSliderChange = (event) => {
            const value = event.target.value;
            this.setSliderValue(value);
        };
        function timeToMinutes(time) {
            const [hours, minutes] = time.split(":").map(num => parseInt(num, 10));
            return hours * 60 + minutes;
        }
        let slider = document.getElementById("timeSlider");

        slider.removeEventListener("input", this.onSliderChangeBound);
        slider.addEventListener("input", onSliderChange);
        
        // บันทึก Reference เพื่อให้สามารถลบ Event Listener ได้ในอนาคต
        this.onSliderChangeBound = onSliderChange;
    
        // ฟังก์ชันตั้งค่า value ของ slider ตามเวลาที่เลือก
        const setSliderPosition = (time) => {
            const timeInMinutes = timeToMinutes(time);
            const index = time_list.findIndex(t => timeToMinutes(t) === timeInMinutes);
            if (index !== -1) {
                this.setSliderValue(index);
            } else {
                console.warn("Selected time not in range!");
            }
        };
    
        // เรียก setSliderPosition เพื่อกำหนดค่า slider
        setSliderPosition(selectedTime);
    }
    
    // ฟังก์ชันตั้งค่า min, max, step ของ slider
    setSliderConfig(min, max, step) {
        let sliderContainer = document.getElementById("rangeSliderContainer");
        let slider = document.getElementById("timeSlider");
    
        slider.min = min;
        slider.max = max;
        slider.step = step;
    
        sliderContainer.style.setProperty('--min', min);
        sliderContainer.style.setProperty('--max', max);
        sliderContainer.style.setProperty('--min-text', `"${this.state.tracking[min].time}"`);
        sliderContainer.style.setProperty('--max-text', `"${this.state.tracking[max].time}"`);
        sliderContainer.style.setProperty('--step', step);
    }
    
    // ฟังก์ชันอัปเดตค่า value ของ slider
    setSliderValue(value) {
        let sliderContainer = document.getElementById("rangeSliderContainer");
        let slider = document.getElementById("timeSlider");
        let output = document.getElementById("timeOutput");
    
        slider.value = value;
    
        sliderContainer.style.setProperty('--value', value);
        // sliderContainer.style.setProperty('--text-value', JSON.stringify(value));
    
        output.textContent = this.state.tracking[value].time;
    }

    
}

TrackingMap.template = "tracking_map_template";
registry.category("actions").add("tracking_map_component", TrackingMap);