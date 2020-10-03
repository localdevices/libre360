// Adjustable parameters
length = 65;
width = 30;
thickness = 2;
screw_hole_radius = 1.25;
screw_hole_offset = 3.5;
pad_diameter = 7;
pad_height = 4;

// Don't touch

pin = pad_height * 2 + 2;


// This is not inches. No need to fix.
difference(){
    union() {
        cube([length,width,thickness], center = true);
        translate([length/2 - screw_hole_offset, width/2 - screw_hole_offset,0]) {
            cylinder( r = pad_diameter/2, h = pad_height, $fn = 64);
        }
        mirror([1,0,0]) {    
            translate([length/2 - screw_hole_offset, width/2 - screw_hole_offset,0]) {
                cylinder( r = pad_diameter/2, h = pad_height, $fn = 64);
            }
        }
        mirror([0,1,0]) {    
            translate([length/2 - screw_hole_offset, width/2 - screw_hole_offset,0]) {
                cylinder( r = pad_diameter/2, h = pad_height, $fn = 64);
            }
        }
        mirror([1,0,0]) {
            mirror([0,1,0]) {    
                translate([length/2 - screw_hole_offset, width/2 - screw_hole_offset,0]) {
                    cylinder( r = pad_diameter/2, h = pad_height, $fn = 64);
                }
            }
        }    
    }

    translate([length/2 - screw_hole_offset, width/2 - screw_hole_offset,-2]) {
            cylinder(r = screw_hole_radius, h = pin, $fn=64);
    }

    mirror([1,0,0]) {    
        translate([length/2 - screw_hole_offset, width/2 - screw_hole_offset,-2]) {
            cylinder(r = screw_hole_radius, h = pin, $fn=64);
        }
    }

    mirror([0,1,0]) {    
        translate([length/2 - screw_hole_offset, width/2 - screw_hole_offset,-2]) {
            cylinder(r = screw_hole_radius, h = pin, $fn=64);
        }
    }

    mirror([1,0,0]) {
        mirror([0,1,0]) {    
            translate([length/2 - screw_hole_offset, width/2 -  screw_hole_offset,-2]) {
                cylinder(r = screw_hole_radius, h = pin, $fn=64);
            }
        }
    }
}