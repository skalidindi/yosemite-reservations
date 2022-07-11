import got from "got";
import twilio from "twilio";
import { format, startOfMonth } from "date-fns";

const BASE_URL = "https://www.recreation.gov";
const {
  START_DATE,
  END_DATE,
  DAYS_TO_INCLUDE,
  TWILIO_ACCOUNT_SID,
  TWILIO_AUTH_TOKEN,
  TWILIO_FROM_NUMBER,
  TWILIO_TO_NUMBER,
} = process.env;

export const handler = async () => {
  const availableCampsites = await getAvailableCampsties(
    START_DATE,
    END_DATE,
    DAYS_TO_INCLUDE.split(",").map((num) => parseInt(num, 10))
  );
  if (Array.isArray(availableCampsites) && availableCampsites.length) {
    let messageBody = "";
    for (const campsite of availableCampsites) {
      messageBody += `\n${campsite.park}, Booking URL: ${campsite.url}, available on ${campsite.date}.\n`;
    }
    await sendTwilio(messageBody);
  } else {
    console.log("No campsites available.");
  }
};

async function getAvailableCampsties(startDate, endDate, daysToInclude) {
  let availableCampsites = [];
  const PARKS = {
    232447: "UPPER PINES",
    232450: "LOWER PINES",
    232449: "NORTH PINES",
  };
  const startOfMonthDate = format(
    startOfMonth(new Date(startDate.split("-"))),
    "yyyy-MM-dd"
  );
  const parkIds = Object.keys(PARKS);
  for (const parkId of parkIds) {
    const campsites = await getCampgroundAvailabilities(
      parkId,
      startOfMonthDate
    );
    const campsiteIds = Object.keys(campsites);
    for (const campsiteId of campsiteIds) {
      availableCampsites = availableCampsites.concat(
        getAvailabilitiesForCampsite(
          PARKS[parkId],
          campsites[campsiteId],
          startDate,
          endDate,
          daysToInclude
        )
      );
    }
  }
  return availableCampsites;
}

function getGotInstance(prefixUrl) {
  return got.extend({
    prefixUrl,
    headers: {
      authority: "www.recreation.gov",
      "user-agent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    },
  });
}

function getCampgroundAvailabilities(parkId, startDate) {
  const START_TIME = "T00%3A00%3A00.000Z";
  const instance = getGotInstance(BASE_URL);
  return instance
    .get(
      `api/camps/availability/campground/${parkId}/month?start_date=${startDate}${START_TIME}`
    )
    .json();
}

function getAvailabilitiesForCampsite(
  park,
  campsiteDetails,
  startDate,
  endDate,
  daysToInclude
) {
  const CAMPSTIES_URL = "/camping/campsites/";
  const PREFERRED_CAMPGROUND_TYPE = "STANDARD NONELECTRIC";
  const AVAILABLE_STATUS = "Available";
  const matchingAvailabilities = [];
  const { availabilities, campsite_type: campsiteType } = campsiteDetails;
  if (campsiteType === PREFERRED_CAMPGROUND_TYPE) {
    for (const [time, reservationStatus] of Object.entries(availabilities)) {
      const date = new Date(time);
      if (
        reservationStatus === AVAILABLE_STATUS &&
        daysToInclude.includes(getDay(date)) &&
        isWithinInterval(date, {
          start: new Date(startDate),
          end: new Date(endDate),
        })
      ) {
        const url = `${BASE_URL}${CAMPSTIES_URL}${campsiteDetails["campsite_id"]}`;
        matchingAvailabilities.push({
          park,
          date: format(new Date(time), "yyyy-MM-dd (EEEE)"),
          url,
        });
      }
    }
  }
  return matchingAvailabilities;
}

export async function sendTwilioMessage(body) {
  const client = new twilio(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN);

  return client.messages.create({
    body,
    to: TWILIO_TO_NUMBER,
    from: TWILIO_FROM_NUMBER,
  });
}
