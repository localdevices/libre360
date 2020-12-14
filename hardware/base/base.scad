// Define dimensions. All in mm

num_cams = 7;

//mid_thickness = 7; // Thickness of inner raised area (first "step")
edge_thickness = 7; // Thickness of the raised edge where the holes are
edge_width_from_hole = 7; // Width of the edge, material on each side of the hole
hole_diameter = 6; // bolt hole diameter
bolthead_d = 10; // bolt head countersink diameter
bolthead_h = 2; // bolt head height (for countersink depth)
radius_to_hole = 50; // Distance from center to the center of the mounting holes
//mid_area_width = 0; // Width of the inner raised area
radius_central_gap = 8.75  ; // Radius of the empty central area
central_gap_thickness = 12.7;
downangle = 25; // Angle in degrees cameras face downward


// Alignment indent in edge
// picam base width is 13.5
picam_base_width = 14.1375 ; 
// picam base thickness is 11.5, optimum size is
// 12.1375, but we want to give a little space for
// bad drilling and it's better to index against
// the side
picam_base_thickness = 12.2;
indent_depth = 4;
offset_of_hole = 0; // If the mounting bolt hole isn't centered you can adjust it
plate_thickness = edge_thickness - indent_depth; // thickness of base plate

// Don't touch
rotate_angle = 360/num_cams;
overhang = edge_width_from_hole + hole_diameter/2;
plate_length = radius_to_hole + overhang;
poly_side = tan(360/(num_cams * 2)) * 2 * (plate_length);
plate_length_hole = radius_central_gap;
poly_side_hole = tan(360/(num_cams * 2)) * 2 * (plate_length_hole);
radius_to_cam_base = radius_to_hole - picam_base_thickness / 2 - offset_of_hole;

// Part
difference(){
    // Body loop
    for (cam = [1 : num_cams]){
        rotate([0, 0, cam * rotate_angle]){
            union(){
                translate([radius_central_gap, -poly_side / 2, 0]){
                    cube([plate_length - radius_central_gap, poly_side, plate_thickness]);
                }
                // Spokes
                translate([radius_central_gap,-poly_side_hole / 2,0]){
                    cube([overhang, poly_side, edge_thickness]);
                }
                // Wheel
                translate([radius_to_hole - overhang,-poly_side / 2,0]){
                    cube([overhang * 2, poly_side, edge_thickness]);
                }
            }
        }
    }
    // Camera mount holes loop
    for (cam = [1 : num_cams]){

	 
        rotate([0,0,cam * rotate_angle + (360/num_cams/1.8)]){
            translate([radius_to_hole, -picam_base_width/2, edge_thickness - indent_depth]){
                rotate([0, downangle, -rotate_angle]){
                    union(){
                        translate([-picam_base_thickness / 2, -picam_base_width / 2, 0]){
                            cube([picam_base_thickness, picam_base_width, indent_depth + 10]);
                        }
                        translate([0, 0, -(bolthead_h * 2 + 10)]){
                            cylinder(r = hole_diameter / 2, h = edge_thickness * 3 + 10, $fn = 64);
                            cylinder(r = bolthead_d / 2 + 0.1, h = bolthead_h + 10, $fn = 64);

                        }
                    }
                }
            }
        }
    }
}



/*  Bolts and Nuts v1.9.6 OpenSCAD Library
    Copyright (C) 2015 Cristiano Gariboldo - Pixel3Design.it

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    
-------------------------------------------------------------------------

    The "nuts_and_bolts.scad" script includes the "threads.scad" library
    coded by Dan Kirshner v2.5 - dan_kirshner@yahoo.com to make it easier for
    those peoples that don't know how to include a new library into
    OpenSCAD and to make it work in the future into the MakerBot
    Customizer.

-------------------------------------------------------------------------
*/

use <threads_2.5.scad>;

function hex_dia (dia) = dia * ( 2 / sqrt (3) ); // return real size for hexagon side to side
function imp (imp_m) = imp_m * 25.4; // return converted imperial -> metric values

module cut_bit (height, radius) { // hegagonal nuts insertion cutout
    $fn = 64;
    union () {
        translate ([0, 0, height / 2]) cylinder (h = height / 2, r1 = hex_dia (radius + (radius * (3 / 10))), r2 = hex_dia (radius - (radius * (2 / 13)))); // top half cone
        translate ([0, 0, 0]) cylinder (h = height / 2, r2 = hex_dia (radius + (radius * (3 / 10))), r1 = hex_dia (radius - (radius * (2 / 13)))); // bottom half cone
    }
}

// EXAMPLES :

render = 1; // Set render at 1 to preview types, set to 0 otherwise.

if ( render == 1 ) 

//    translate ([0, 0, 0]) hex_bolt (1, 5/8, 0, 3/8, 1/128, 64, 1, "imperial", 11);

    translate ([0, 0, 0]) hex_nut (3/4, 5/8, 29/32, 1/128, 64, 1, "imperial", 11);


module conical_allen_bolt (height = 30, width = 6, head_size = 14, head_height = 8, tolerance = 0.2, quality = 32, thread, bool_round, allen_o, thread_len, pitch) {
    union () {
        $fn = quality;
        if ( thread ) {
            if ( thread == "metric" ) {
                translate ([0,0,thread_len]) cylinder (h=height-thread_len, r=(width/2)-tolerance, $fn=32);
                if ( thread_len ) {
                    metric_thread (width-tolerance, pitch, thread_len);
                }
                else {
                    cylinder (r = width / 2, h = thread_len );
                }
                translate ([0,0,height-0.001]) head_conical_allen (head_size-tolerance, head_height, quality, bool_round, allen_o + tolerance);
            }
            else {
                thread_len_i = imp (thread_len);
                height = imp (height);
                width_i = imp (width);
                tolerance_i = imp (tolerance);
                allen_o = imp (allen_o);
                head_size = imp (head_size);
                head_height = imp (head_height);
                translate ([0,0,thread_len_i]) cylinder (h=height-thread_len_i, r=(width_i/2)-tolerance_i, $fn=32);
                english_thread (width-tolerance, pitch, thread_len);
                translate ([0,0,height-0.001]) head_conical_allen (head_size-tolerance_i, head_height, quality, bool_round, allen_o+tolerance_i);
            }
        }
        else {
            //translate ([0,0,thread_len]) cylinder (h=height-thread_len, r=(width/2)-tolerance, $fn=32);
            cylinder (h = height, r = (width-tolerance) / 2, $fn = quality / 2);
            //metric_thread (width-tolerance, pitch, thread_len);
            translate ([0,0,height-0.001]) head_conical_allen (head_size-tolerance, head_height, quality, bool_round, allen_o + tolerance);
        }
    }
}

module hex_nut (height, thread_d, size, tolerance, quality, bool_cut, thread, pitch) {
    difference () {
        $fn = 6; // make it "hex"
        if ( thread ) { // is set?
            if ( thread == "metric" ) { // is metric?
                if ( bool_cut ) {
                    intersection() { // making "the Nut"
                        cylinder (r = hex_dia (size - tolerance) / 2, h = height); // hex nut
                        cut_bit (height, size / 2); // cutout
                    }
                }
                else {
                    cylinder (r = hex_dia (size - tolerance) / 2, h = height); // hex nut
                }
            } 
            if ( thread == "imperial" ) { // is imperial?
                size = imp (size); // imperial -> metric
                height = imp (height); // imperial -> metric
                tolerance = imp (tolerance); // imperial -> metric
                if ( bool_cut ) {
                    intersection() { // making "the Nut"
                        cylinder (r = hex_dia (size - tolerance) / 2, h = height); // hex nut
                        cut_bit (height, size / 2); // cutout
                    }
                }
                else {
                    cylinder (r = hex_dia (size - tolerance) / 2, h = height); // hex nut
                }
            }
        }
        // cut part
        if ( thread ) { // is set?
            if ( thread == "metric" ) { // is metric?
                $fn = quality; // set the quality
                translate ([0, 0, -1]) {
                    if ( pitch ) {
                        metric_thread (thread_d + tolerance, pitch, height + 2); // thread it!
                    }
                    else {
                        $fn = quality / 2;
                        cylinder (r = (thread_d + tolerance) / 2, height + 2); // a dummy cylindric bar
                    }
                }
            } 
            if ( thread == "imperial" ) { // is imperial?
                $fn = quality ; // set the quality
                translate ([0, 0, -1]) {
                    if ( pitch ) {
                        english_thread (thread_d + tolerance, pitch, height + (1/10)); // thread it!
                    }
                    else {
                        $fn = quality / 2; // half declared quality
                        thread_d = imp (thread_d);
                        tolerance = imp (tolerance);
                        height = imp (height);
                        cylinder (r = (thread_d + tolerance) / 2, height + 2); // a dummy cylindric bar
                    }
                }
            }
        } else {
            $fn = quality / 2; // half declared quality
            translate ([0, 0, -1]) cylinder (r = (thread_d + tolerance) / 2, height + 2); // a dummy cylindric bar
        }
    }
}

module grub_bolt (length, thread_d, a_depth, tolerance, quality, allen_o, thread, pitch) {
    difference () {
        union () {
            if ( thread ) {
                if ( thread == "metric" ) {
                    $fn = quality;
                    metric_thread (thread_d - tolerance, pitch, length);
                }
                if ( thread == "imperial" ) {
                    $fn = quality;
                    english_thread (thread_d - tolerance, pitch, length);
                }
            } else {
                $fn = quality / 2;
                cylinder (r = (thread_d - tolerance) / 2, h = length);
            }
        }
        if ( allen_o ) {
            $fn = 6;
            if ( thread ) {
                if ( thread == "metric" ) {
                    translate ([0, 0, length - a_depth + 0.5]) cylinder (h = a_depth, r = hex_dia (allen_o + tolerance) / 2);
                }
                if ( thread == "imperial" ) {
                    length = imp (length);
                    a_depth = imp (a_depth);
                    allen_o = imp (allen_o);
                    tolerance = imp (tolerance);
                    translate ([0, 0, length - a_depth + 0.5]) cylinder (h = a_depth, r = hex_dia (allen_o + tolerance) / 2);
                }
            } else {
                
                    translate ([0, 0, length - a_depth + 0.5]) cylinder (h = a_depth, r = hex_dia (allen_o + tolerance) / 2);
            }
        }
    }
}

module hex_bolt (length, thread_d, head_h, head_d, tolerance, quality, bool_cut, thread, pitch) {
    union () {
        if ( thread ) {
            if ( thread == "metric" ) {
                $fn = quality;
                if ( pitch ) {
                    metric_thread (thread_d - tolerance, pitch, length);
                } else {
                    $fn = quality / 2;
                    cylinder (r = (thread_d - tolerance) / 2, h = length);
                }
            }
            if ( thread == "imperial" ) {
                $fn = quality;
                if ( pitch ) {
                    english_thread (thread_d - tolerance, pitch, length);
                } else {
                    $fn = quality / 2;
                    thread_d = imp(thread_d);
                    tolerance = imp(tolerance);
                    length = imp(length);
                    cylinder (r = (thread_d - tolerance) / 2, h = length);
                }
            }
        } else {
            $fn = quality / 2;
            cylinder (r = (thread_d - tolerance) / 2, h = length);
        }
        $fn = 6;
        if ( thread ) {
            if ( thread == "imperial" ) {
                length = imp (length);
                head_d = imp (head_d);
                head_h = imp (head_h);
                tolerance = imp (tolerance);
                translate ([0, 0, length]) {
                    if ( bool_cut == 1 ) {
                        intersection() {
                            cylinder (r = hex_dia (head_d - tolerance) / 2, h = head_h);
                            cut_bit (head_h, head_d/2);
                        }
                    } else {
                        cylinder (r = hex_dia (head_d - tolerance) / 2, h = head_h);
                    }
                }
            }
            if ( thread == "metric" ) {
                translate ([0, 0, length]) {
                    if ( bool_cut == 1 ) {
                        intersection() {
                            cylinder (r = hex_dia (head_d - tolerance) / 2, h = head_h);
                            cut_bit (head_h, head_d/2);
                        }
                    } else {
                        cylinder (r = hex_dia (head_d - tolerance) / 2, h = head_h);
                    }
                }
            }
        } else {
            translate ([0, 0, length]) {
                intersection() {
                    cylinder (r = hex_dia (head_d - tolerance) / 2, h = head_h);
                    cut_bit (head_h, head_d/2);
                }
            }
        } 
    }   
}

module cone_head_bolt (length, thread_d, head_h, head_d, a_depth, tolerance, quality, allen_o, thread, pitch) {
    difference () {
        union () {
            if ( thread ) {
                if ( thread == "metric" ) {
                    $fn = quality;
                    metric_thread (thread_d - tolerance, pitch, length);
                }
                if ( thread == "imperial" ) {
                    $fn = quality;
                    english_thread (thread_d - tolerance, pitch, length);
                }
            } else {
                $fn = quality / 2;
                cylinder (r = (thread_d - tolerance) / 2, h = length);
            }
            if ( thread ) {
                if ( thread == "imperial" ) {
                    $fn = quality;
                    thread_d = imp (thread_d);
                    head_d = imp (head_d);
                    head_h = imp (head_h);
                    tolerance = imp (tolerance);
                    minkowski () {
                        sphere (r = (1 / 8) * ((thread_d - tolerance) / 2));
                        translate ([0, 0, length]) cylinder (r1 = (thread_d / 2) - ((1 / 8) * ((thread_d - tolerance) / 2)), r2 = ((head_d - tolerance) / 2) - ((1 / 8) * ((head_d - tolerance) / 2)), h = head_h + tolerance);
                    }
                }
                if ( thread == "metric" ) {
                    $fn = quality;
                    minkowski () {
                        sphere (r = (1 / 8) * ((thread_d - tolerance) / 2));
                        translate ([0, 0, length]) cylinder (r1 = (thread_d / 2) - ((1 / 8) * ((thread_d - tolerance) / 2)), r2 = ((head_d - tolerance) / 2) - ((1 / 8) * ((head_d - tolerance) / 2)), h = head_h + tolerance);
                    }
                }
            } else {
                minkowski () {
                    $fn = quality / 2;
                    sphere (r = (1 / 8) * ((thread_d - tolerance) / 2));
                    translate ([0, 0, length]) cylinder (r1 = (thread_d / 2) - ((1 / 8) * ((thread_d - tolerance) / 2)), r2 = ((head_d - tolerance) / 2) - ((1 / 8) * ((head_d - tolerance) / 2)), h = head_h + tolerance);
                    }
            }
        }
        if ( allen_o ) {
            $fn = 6;
            if ( thread ) {
                if ( thread == "imperial" ) {
                    length = imp (length);
                    head_h = imp (head_h);
                    a_depth = imp (a_depth);
                    allen_o = imp (allen_o);
                    tolerance = imp (tolerance);
                    translate ([0, 0, (length + head_h) - (a_depth - 0.5)]) cylinder (h = a_depth, r = hex_dia (allen_o + tolerance) / 2);
                }
                if ( thread == "metric" ) {
                    translate ([0, 0, (length + head_h) - (a_depth - 0.5)]) cylinder (h = a_depth, r = hex_dia (allen_o + tolerance) / 2);
                }
            } else {
                translate ([0, 0, (length + head_h) - (a_depth - 0.5)]) cylinder (h = a_depth, r = hex_dia (allen_o + tolerance) / 2);
            }
        }
    }
}

module allen_bolt (length, thread_d, head_h, head_d, a_depth, tolerance, quality, bool_round, allen_o, thread, pitch) {
    difference () {
        union () {
            if ( thread ) {
                if ( thread == "metric" ) {
                    $fn = quality;
                    metric_thread (thread_d - tolerance, pitch, length);
                }
                if ( thread == "imperial" ) {
                    $fn = quality;
                    english_thread (thread_d - tolerance, pitch, length);
                }
            } else {
                $fn = quality / 2;
                cylinder (r = (thread_d - tolerance) / 2, h = length);
            }
            if ( thread ) {
                if ( thread == "metric" ) {
                    if ( bool_round ) {
                        $fn = quality;
                        minkowski () {
                            sphere (r = (1 / 8) * ((head_d - tolerance) / 2));
                            translate ([0, 0, length]) cylinder (h = head_h - tolerance, r = ((head_d - tolerance) / 2) - ((1 / 8) * ((head_d - tolerance) / 2)));
                        }
                    } else {
                        $fn = quality / 2;
                        translate ([0, 0, length]) cylinder (h = head_h - tolerance, r = (head_d - tolerance) / 2);
                    }
                }
                if ( thread == "imperial" ) {
                    head_d = imp (head_d);
                    length = imp (length);
                    tolerance = imp (tolerance);
                    if ( bool_round ) {
                        $fn = quality;
                        minkowski () {
                            sphere (r = (1 / 8) * ((head_d - tolerance) / 2));
                            translate ([0, 0, length]) cylinder (h = head_h - tolerance, r = ((head_d - tolerance) / 2) - ((1 / 8) * ((head_d - tolerance) / 2)));
                        }
                    } else {
                        $fn = quality / 2;
                        translate ([0, 0, length]) cylinder (h = head_h - tolerance, r = (head_d - tolerance) / 2);
                    }
                }
            } else {
                if ( bool_round ) {
                    $fn = quality;
                    minkowski () {
                        sphere (r = (1 / 8) * ((head_d - tolerance) / 2));
                        translate ([0, 0, length]) cylinder (h = head_h - tolerance, r = ((head_d - tolerance) / 2) - ((1 / 8) * ((head_d - tolerance) / 2)));
                    }
                } else {
                    $fn = quality / 2;
                    translate ([0, 0, length]) cylinder (h = head_h - tolerance, r = (head_d - tolerance) / 2);
                }
            }
        }
        if ( allen_o ) {
            $fn = 6;
            if ( thread ) {
                if ( thread == "imperial" ) {
                    length = imp (length);
                    head_h = imp (head_h);
                    a_depth = imp (a_depth);
                    allen_o = imp (allen_o);
                    tolerance = imp (tolerance);
                    translate ([0, 0, (length + head_h) - (a_depth - 0.5)]) cylinder (h = a_depth, r = hex_dia (allen_o + tolerance) / 2);
                }
                if ( thread == "metric" ) {
                    translate ([0, 0, (length + head_h) - (a_depth - 0.5)]) cylinder (h = a_depth, r = hex_dia (allen_o + tolerance) / 2);
                }
            } else {
                translate ([0, 0, (length + head_h) - (a_depth - 0.5)]) cylinder (h = a_depth, r = hex_dia (allen_o + tolerance) / 2);
            }
        }
    }
}

module washer (outer, inner, width, tolerance, quality, thread) {
    $fn = quality;
    if ( thread ) {
        if ( thread == "metric") {
            difference () {
                cylinder (r = (outer - tolerance) / 2, h = width);
                translate ([0, 0, -1]) cylinder (r = (inner + tolerance) / 2, h = width + 2);
            }
        }
        if ( thread == "imperial" ) {
            outer = imp (outer);
            inner = imp (inner);
            width = imp (width);
            tolerance = imp (tolerance);
            difference () {
                cylinder (r = (outer - tolerance) / 2, h = width);
                translate ([0, 0, -1]) cylinder (r = (inner + tolerance) / 2, h = width + 2);
            }
        } else {
            difference () {
                cylinder (r = (outer - tolerance) / 2, h = width);
                translate ([0, 0, -1]) cylinder (r = (inner + tolerance) / 2, h = width + 2);
            }
        }
    }
}

module head_conical_allen (width = 10, height = 5, quality = 32, bool_round, allen_o) {
    if ( allen_o ) {
        difference () {
            if ( bool_round == 1 ) {
                minkowski () {
                    $fn = quality;
                    sphere ((1/32)*width);
                    cylinder (h=height-(1/32)*width, r1=(width-((1/32)*width))/2, r2=((width*(4/5))-((1/32)*width))/2);
                }
            }
            if ( bool_round == 0 ) {
                $fn = quality / 2;
                cylinder (h=height, r1=width/2, r2=(width*(4/5))/2);
            }
            translate ([0,0,height*(2/7)]) cylinder (h=height*(3/4), r=(allen_o/(2/sqrt(3)))/2, $fn=6);
        }
    }
    else {
        $fn = quality / 2;
        cylinder (h=height, r1=width/2, r2=(width*(4/5))/2);
    }
}

/* From http://www.thingiverse.com/thing:3457
   © 2010 whosawhatsis

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU Lesser General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
   GNU Lesser General Public License for more details.

   You should have received a copy of the GNU Lesser General Public License
   along with this program. If not, see <http://www.gnu.org/licenses/>.
*/


/*
This script generates a teardrop shape at the appropriate angle to prevent overhangs greater than 45 degrees. The angle is in degrees, and is a rotation around the Y axis. You can then rotate around Z to point it in any direction. Rotation around X or Y will cause the angle to be wrong.
*/

module teardrop(radius, length, angle) {
	rotate([0, angle, 0]) union() {
		linear_extrude(height = length, center = true, convexity = radius, twist = 0)
			circle(r = radius, center = true, $fn = 30);
		linear_extrude(height = length, center = true, convexity = radius, twist = 0)
			projection(cut = false) rotate([0, -angle, 0]) translate([0, 0, radius * sin(45) * 1.5]) cylinder(h = radius * sin(45), r1 = radius * sin(45), r2 = 0, center = true, $fn = 30);
	}
}
