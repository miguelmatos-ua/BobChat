package main

import (
	"fmt"
	"github.com/PuerkitoBio/goquery"
	"io/ioutil"
	"net/http"
	"os"
	"strings"
	"time"
)

type Election struct {
	Country      string
	ElectionType string
	BeginDate    time.Time
	EndDate      time.Time
}

// Download the page and cast it to a BeautifulSoup object
func DownloadPage(url string) (*goquery.Document, error) {
	client := &http.Client{}
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("User-Agent", "Thunder Client (https://www.thunderclient.com)")
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	return goquery.NewDocumentFromReader(strings.NewReader(string(body)))
}

// Parse the page into a dictionary with the elections information
func ParsePage(doc *goquery.Document) []Election {
	year := doc.Find("td[colspan='3']:nth-child(2)").Text()

	var result []Election

	doc.Find("table tr").Each(func(i int, row *goquery.Selection) {
		cells := row.Find("td")
		if cells.Length() < 3 {
			return
		}

		country := cells.Eq(0).Text()
		electionType := cells.Eq(1).Text()
		dateStr := cells.Eq(2).Text() + " " + year
		dates := GetDateRange(dateStr)

		election := Election{
			Country:      country,
			ElectionType: electionType,
			BeginDate:    dates["begin_date"],
			EndDate:      dates["end_date"],
		}
		result = append(result, election)
	})

	return result
}

// From a string, return a dictionary with the start and end of an election.
func GetDateRange(str string) map[string]time.Time {
	dateLayout := "2 January 2006"
	dateStrs := strings.Split(str, " ")
	var beginDate, endDate time.Time

	if strings.Contains(dateStrs[0], "-") {
		rangeDays := strings.Split(dateStrs[0], "-")
		beginDay, endDay := rangeDays[0], rangeDays[1]
		beginDateStr := beginDay + " " + dateStrs[1] + " " + dateStrs[2]
		endDateStr := endDay + " " + dateStrs[1] + " " + dateStrs[2]
		beginDate, _ = time.Parse(dateLayout, beginDateStr)
		endDate, _ = time.Parse(dateLayout, endDateStr)
		endDate = endDate.AddDate(0, 0, 1) // add one day
	} else {
		beginDate, _ = time.Parse(dateLayout, str)
		endDate = beginDate.AddDate(0, 0, 1) // add one day
	}

	return map[string]time.Time{
		"begin_date": beginDate,
		"end_date":   endDate,
	}
}

// Generate an ICS file with the election dates
func GenerateIcsFile(elections []Election) {
	file, err := os.Create("elections.ics")
	if err != nil {
		fmt.Println(err)
		return
	}
	defer file.Close()

	file.WriteString("BEGIN:VCALENDAR\n")
	file.WriteString("PRODID:-//BobChat//European Elections v1.0//EN\n")
	file.WriteString("VERSION:2.0\n")
	file.WriteString("CALSCALE:GREGORIAN\n")
	file.WriteString("METHOD:PUBLISH\n")
	file.WriteString("X-WR-CALNAME:Eleições na Europa\n")
	file.WriteString("X-WR-TIMEZONE:UTC\n")
	file.WriteString("X-WR-CALNAME:Eleições na Europa\n")

	for _, elec := range elections {
		beginDate := elec.BeginDate
		endDate := elec.EndDate
		electionType := elec.ElectionType
		country := elec.Country

		file.WriteString("BEGIN:VEVENT\n")
		file.WriteString(fmt.Sprintf("DTSTART;VALUE=DATE:%s\n", beginDate.Format("20060102")))
		file.WriteString(fmt.Sprintf("DTEND;VALUE=DATE:%s\n", endDate.Format("20060102")))
		file.WriteString("CLASS:PUBLIC\n")
		file.WriteString(fmt.Sprintf("DESCRIPTION:%s\n", electionType))
		file.WriteString(fmt.Sprintf("SUMMARY:%s Elections 🗳️\n", country))
		file.WriteString("TRANSP:TRANSPARENT\n")
		file.WriteString("END:VEVENT\n")
	}

	file.WriteString("END:VCALENDAR")
}

func main() {
	uri := "https://europeelects.eu/calendar"
	resp, err := http.Get(uri)
	if err != nil {
		fmt.Println("Error downloading page:", err)
		return
	}
	defer resp.Body.Close()

	doc, err := goquery.NewDocumentFromReader(resp.Body)
	if err != nil {
		fmt.Println("Error parsing page:", err)
		return
	}

	elections := ParsePage(doc)

	GenerateIcsFile(elections)

	fmt.Println("ICS file generated successfully!")
}
