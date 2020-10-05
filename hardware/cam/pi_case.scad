// Adjustable parameters
length_pi_case = 65;
width_pi_case = 30;
thickness = 2;
screw_hole_radius = 1.25;
screw_hole_offset = 3.5;
pad_diameter = 7;
pad_height = 6;
length_cam_case = 38;
width_cam_case = 38;
offset_distance = 7;
offset_hole_distance = offset_distance + length_cam_case / 2;

// Don't touch

pin = pad_height * 2 + 2;


// This is not inches. No need to fix.
difference(){
    union() {
        cube([length_pi_case,width_pi_case,thickness], center = true);
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

    translate([length_pi_case/2 - screw_hole_offset, width_pi_case/2 - screw_hole_offset,-2]) {
            cylinder(r = screw_hole_radius, h = pin, $fn=64);
    }

    mirror([1,0,0]) {    
        translate([length_pi_case/2 - screw_hole_offset, width_pi_case/2 - screw_hole_offset,-2]) {
            cylinder(r = screw_hole_radius, h = pin, $fn=64);
        }
    }

    mirror([0,1,0]) {    
        translate([length_pi_case/2 - screw_hole_offset, width_pi_case/2 - screw_hole_offset,-2]) {
            cylinder(r = screw_hole_radius, h = pin, $fn=64);
        }
    }

    mirror([1,0,0]) {
        mirror([0,1,0]) {    
            translate([length_pi_case/2 - screw_hole_offset, width_pi_case/2 -  screw_hole_offset,-2]) {
                cylinder(r = screw_hole_radius, h = pin, $fn=64);
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