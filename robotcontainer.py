import wpilib
from wpilib.interfaces import GenericHID

import rev

import commands2
import commands2.button

import constants

from commands.complexauto import ComplexAuto
from commands.drivedistance import DriveDistance
from commands.defaultdrive import DefaultDrive
from commands.halvedrivespeed import HalveDriveSpeed
from commands.lucautocommand import LucAutoCommand
from commands.lucautocommandInverted import LucAutoCommand2
from commands.newPath import newPath
from commands.newPathInverted import newPathInverted

from commands.SnowVeyerCommands.DropOff import dropOff
from commands.SnowVeyerCommands.PickUp import pickUp
from commands.SnowVeyerCommands.intake import Intake
from commands.SnowVeyerCommands.outtake import Outtake


from commands.climbingCommands.moveRotateArm import MoveRotateArm
from commands.climbingCommands.moveLiftArm import MoveLiftArm
from commands.climbingCommands.moveLiftArmToLimitSwitch import MoveLiftArmToLimitSwitch
from commands.climbingCommands.moveLiftArmPastLocation import MoveLiftArmPastLocation
from commands.climbingCommands.liftArmToTop import LiftArmToTop

from subsystems.drivesubsystem import DriveSubsystem
from subsystems.snowveyorsubsystem import SnowveyorSubsystem
from subsystems.climbingsubsystem import ClimbingSubsystem

class RobotContainer:
    """
    This class is where the bulk of the robot should be declared. Since Command-based is a
    "declarative" paradigm, very little robot logic should actually be handled in the :class:`.Robot`
    periodic methods (other than the scheduler calls). Instead, the structure of the robot (including
    subsystems, commands, and button mappings) should be declared here.
    """

    def __init__(self) -> None:

        # The driver's controller
        self.driverController = wpilib.XboxController(constants.kDriverControllerPort)
        # self.driverController = wpilib.Joystick(constants.kDriverControllerPort)
        self.operatorController = wpilib.XboxController(constants.kSnowveyorControllerPort)

        # The robot's subsystems
        self.drive = DriveSubsystem()
        self.snowveyor = SnowveyorSubsystem()
        self.climb = ClimbingSubsystem()

        # Autonomous routines

        # A simple auto routine that drives forward a specified distance, and then stops.
        self.simpleAuto = DriveDistance(
            constants.kAutoDriveDistanceInches, constants.kAutoDriveSpeed, self.drive
        )

        # A complex auto routine that drives forward, and then drives backward.
        self.complexAuto = ComplexAuto(self.drive)

        # A complex auto routine that drives forward, and then drives backward.
        self.lucAutoCommand = LucAutoCommand(self.drive, self.snowveyor)
        self.lucAutoCommand2 = LucAutoCommand2(self.drive, self.snowveyor)
        #simpler auto routine that drives to the second ball and places 2 into the smaller hub
        self.newPath = newPath(self.drive, self.snowveyor)
        self.newPathInverted = newPathInverted(self.drive, self.snowveyor)

        # Chooser
        self.chooser = wpilib.SendableChooser()

        # Add commands to the autonomous command chooser
        # self.chooser.setDefaultOption("Complex Auto", self.complexAuto)
        # self.chooser.addOption("Simple Auto", self.simpleAuto)
        self.chooser.addOption("Luc Auto", self.lucAutoCommand)
        self.chooser.addOption("Luc AutoInverted", self.lucAutoCommand2)
        self.chooser.addOption("SimplePath", self.newPath)
        self.chooser.addOption("SimplePathInverted", self.newPathInverted)
        # Put the chooser on the dashboard
        wpilib.SmartDashboard.putData("Autonomous", self.chooser)

        self.configureButtonBindings()

        # set up default drive command
        # self.drive.setDefaultCommand(
        #     DefaultDrive(
        #         self.drive,
        #         lambda: -self.driverController.getRightY(),
        #         lambda: self.driverController.getLeftY(),
        #     )
        # )

    def configureButtonBindings(self):
        """
        Use this method to define your button->command mappings. Buttons can be created by
        instantiating a :GenericHID or one of its subclasses (Joystick or XboxController),
        and then passing it to a JoystickButton.
        """
        commands2.button.JoystickButton(self.operatorController, wpilib.XboxController.Button.kY).whenHeld(
            MoveLiftArm(.5, self.climb)
        )
        commands2.button.JoystickButton(self.operatorController, wpilib.XboxController.Button.kA).whenHeld(
            MoveLiftArm(-.5, self.climb)
        )
        commands2.button.JoystickButton(self.operatorController, wpilib.XboxController.Button.kX).whenHeld(
            MoveRotateArm(.5, self.climb)
        )
        commands2.button.JoystickButton(self.operatorController, wpilib.XboxController.Button.kB).whenHeld(
            MoveRotateArm(-.5, self.climb)
        )
        # commands2.button.JoystickButton(self.operatorController, wpilib.XboxController.Button.kY).whenPressed(
        #     MoveLiftArmToLimitSwitch(.5, self.climb)
        # )
        # commands2.button.JoystickButton(self.operatorController, wpilib.XboxController.Button.kX).whenPressed(
        #     MoveLiftArmPastLocation(-500, False, .5, self.climb)
        # )
        # commands2.button.JoystickButton(self.operatorController, wpilib.XboxController.Button.kB).whenPressed(
        #     LiftArmToTop(self.climb)
        # )
        commands2.button.JoystickButton(self.operatorController, wpilib.XboxController.Button.kLeftBumper).whenHeld(
            Intake(1.0, self.snowveyor)
        )
        commands2.button.JoystickButton(self.operatorController, wpilib.XboxController.Button.kRightBumper).whenHeld(
            Outtake(1.0, self.snowveyor)
        )
        # commands2.button.JoystickButton(self.driverController, 3).whenHeld(
        #     HalveDriveSpeed(self.drive)
        # )

    def getAutonomousCommand(self) -> commands2.Command:
        return self.chooser.getSelected()
