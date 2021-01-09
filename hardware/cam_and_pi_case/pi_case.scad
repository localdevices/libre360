// Adjustable parameters
length_pi_case = 65;
width_pi_case = 30;
thickness = 2;
screw_hole_radius = 1.25;
screw_hole_offset = 3.5;
pad_height = 6;
length_cam_case = 37;
width_cam_case = 37;
offset_distance = 0;
offset_hole_distance = offset_distance + length_cam_case / 2;
nut_diameter = 4.82;
nut_seat_depth = 3;
pad_diameter = 3 + nut_diameter;

// Don't touch

pin = pad_height * 2 + 2;

module pi_corners(pad_height) {
    translate([length_pi_case/2 - screw_hole_offset, width_pi_case/2 - screw_hole_offset,0]) {
    cylinder( r = pad_diameter/2, h = pad_height, $fn = 64);
        
}
    mirror([1,0,0]) {    
        translate([length_pi_case/2 - screw_hole_offset, width_pi_case/2 - screw_hole_offset,0]) {
            cylinder( r = pad_diameter/2, h = pad_height, $fn = 64);
        }
    }
    mirror([0,1,0]) {    
        translate([length_pi_case/2 - screw_hole_offset, width_pi_case/2 - screw_hole_offset,0]) {
            cylinder( r = pad_diameter/2, h = pad_height, $fn = 64);
        }
    }
    mirror([1,0,0]) {
        mirror([0,1,0]) {    
            translate([length_pi_case/2 - screw_hole_offset, width_pi_case/2 - screw_hole_offset,0]) {
                cylinder( r = pad_diameter/2, h = pad_height, $fn = 64);
            }
        }
    } 
}

// This is not inches. No need to fix.
difference(){
    union() {
        hull(){pi_corners(thickness);}
        pi_corners(pad_height);
   
    }

    translate([length_pi_case/2 - screw_hole_offset, width_pi_case/2 - screw_hole_offset,-0.1]) {
            cylinder(r = screw_hole_radius, h = pin, $fn=64);
            cylinder(r = nut_diameter/2, h = nut_seat_depth, $fn=6);
    }

    mirror([1,0,0]) {    
        translate([length_pi_case/2 - screw_hole_offset, width_pi_case/2 - screw_hole_offset,-0.1]) {
            cylinder(r = screw_hole_radius, h = pin, $fn=64);
            cylinder(r = nut_diameter/2, h = nut_seat_depth, $fn=6);
        }
    }

    mirror([0,1,0]) {    
        translate([length_pi_case/2 - screw_hole_offset, width_pi_case/2 - screw_hole_offset,-0.1]) {
            cylinder(r = screw_hole_radius, h = pin, $fn=64);
            cylinder(r = nut_diameter/2, h = nut_seat_depth, $fn=6);            
        }
    }

    mirror([1,0,0]) {
        mirror([0,1,0]) {    
            translate([length_pi_case/2 - screw_hole_offset, width_pi_case/2 -  screw_hole_offset,-0.1]) {
                cylinder(r = screw_hole_radius, h = pin, $fn=64);
                cylinder(r = nut_diameter/2, h = nut_seat_depth, $fn=6);
            }
        }
    }

    translate([length_pi_case/2 - offset_hole_distance, width_cam_case/4 ,-2]) {
        cylinder(r = screw_hole_radius, h = pin, $fn=64);
    }

    mirror([0,1,0]) {    
        translate([length_pi_case/2 - offset_hole_distance, width_cam_case/4 ,-2]) {
            cylinder(r = screw_hole_radius, h = pin, $fn=64);
        }
    }  

}